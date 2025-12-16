import json
import os
import random
import re
from typing import Any, TypedDict, cast

import chess
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from src.config import (
    FALLBACK_COMMENTARY,
    LLM_COMMENTATOR_TEMPERATURE,
    LLM_DEFAULT_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_STOP_TOKENS,
    LLM_STRATEGIST_TEMPERATURE,
    MAX_RETRIES,
)
from src.logger import logger

load_dotenv()


def get_llm(
    temperature: float = LLM_DEFAULT_TEMPERATURE,
    max_tokens: int = LLM_MAX_TOKENS,
) -> ChatOpenAI:
    """
    Factory for the LLM client.
    """
    return ChatOpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=cast("Any", os.getenv("LLM_API_KEY")),
        model=os.getenv("LLM_MODEL") or "",
        temperature=temperature,
        extra_body={"max_tokens": max_tokens, "stop": LLM_STOP_TOKENS},
    )


llm_strategist = get_llm(temperature=LLM_STRATEGIST_TEMPERATURE)
llm_commentator = get_llm(temperature=LLM_COMMENTATOR_TEMPERATURE)


class AgentState(TypedDict):
    fen: str
    legal_moves_uci: list[str]
    history_pgn: str

    # Internal
    thought_process: str | None
    proposed_move: str | None
    error_message: str | None
    retry_count: int

    # Output
    final_move_uci: str | None
    commentary: str | None


def extract_json(text: str):
    """
    Extract JSON from text, even if the model adds a preamble.
    Looks for the first {...} block.
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return None
    except Exception:
        return None


def strategist_node(state: AgentState):
    """
    Strategist agent with Chain-of-Thought (CoT) enabled.
    """
    fen = state["fen"]
    error = state.get("error_message", "")
    retries = state["retry_count"]

    system_prompt = (
        "You are a professional Chess Engine."
        "\nTASK: Analyze the board state and choose the best move."
        "\nFORMAT: "
        "\n1. First, think step-by-step. Analyze threats, candidates, and strategy."
        '\n2. Then, output the selected move inside a JSON block: {"move": "e2e4"}.'
        "\nIMPORTANT: The JSON must be at the very end."
    )

    user_prompt = f"Current FEN: {fen}"

    if error:
        user_prompt += (
            f"\n\nCRITICAL ERROR: Your previous move was REJECTED by the Arbiter."
            f"\nReason: {error}"
            f"\nAttempts used: {retries}/10."
            f"\nTask: Choose a DIFFERENT, LEGAL move from the candidates."
        )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    try:
        response = llm_strategist.invoke(messages)
        raw_content = response.content
        # Fallback: convert non-string content (e.g. tool calls) into JSON text
        content = raw_content.strip() if isinstance(raw_content, str) else json.dumps(raw_content, ensure_ascii=False)

        logger.info(f"🧠 STRATEGIST THOUGHTS:\n{content}")

        data = extract_json(content)

        if not data or "move" not in data:
            logger.warning("Failed to extract JSON from response")
            return {
                "error_message": 'Invalid JSON format. I need {"move": "..."}',
                "retry_count": retries + 1,
                "thought_process": content,
            }

        move = data.get("move")

        return {
            "proposed_move": move,
            "retry_count": retries + 1,
            "thought_process": content,
        }

    except Exception as e:
        logger.error(f"Strategist exception: {e}")
        return {"error_message": f"Internal Error: {e!s}", "retry_count": retries + 1}


def arbiter_node(state: AgentState):
    """
    Validator node that checks legality of the move.
    """
    proposed = state["proposed_move"]
    legal_moves = state["legal_moves_uci"]

    if not proposed:
        return {"error_message": "No move found"}

    proposed = proposed.lower().strip()

    if proposed in legal_moves:
        logger.info(f"✅ Arbiter approved: {proposed}")
        return {"final_move_uci": proposed, "error_message": None}
    logger.warning(f"❌ Arbiter rejected: {proposed} (not in legal moves)")
    return {
        "error_message": f"Move '{proposed}' is ILLEGAL. Legal moves are: {legal_moves[:10]}...",
        "proposed_move": None,
    }


def commentator_node(state: AgentState):
    move = state["final_move_uci"]
    fen = state["fen"]
    retries = state["retry_count"]
    thoughts = state.get("thought_process", "")

    system_prompt = (
        "You are a Chess Commentator."
        "You have access to the player's internal thoughts and the board state."
        "Make a short, witty remark about the move."
    )

    prompt = f"Move played: {move}. FEN: {fen}."

    if retries > 1:
        prompt += f"\nNote: The AI struggled and failed {retries - 1} times before finding this move. Make fun of that."

    if thoughts:
        prompt += f"\nAI's Internal Monologue snippet: {thoughts[:200]}..."

    try:
        response = llm_commentator.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ],
        )
        return {"commentary": response.content}
    except Exception:
        return {"commentary": "..."}


workflow = StateGraph(AgentState)
workflow.add_node("strategist", strategist_node)
workflow.add_node("arbiter", arbiter_node)
workflow.add_node("commentator", commentator_node)

workflow.set_entry_point("strategist")


def should_retry(state: AgentState):
    if state.get("final_move_uci"):
        return "commentator"
    if state["retry_count"] > MAX_RETRIES:
        return "force_random"
    return "strategist"


workflow.add_conditional_edges(
    "arbiter",
    should_retry,
    {
        "strategist": "strategist",
        "commentator": "commentator",
        "force_random": END,
    },
)

workflow.add_edge("strategist", "arbiter")
workflow.add_edge("commentator", END)

app_agent = workflow.compile()


def get_agent_move(board: chess.Board):
    legal_moves = [m.uci() for m in board.legal_moves]

    initial_state: AgentState = {
        "fen": board.fen(),
        "legal_moves_uci": legal_moves,
        "history_pgn": "",
        "retry_count": 0,
        "error_message": None,
        "proposed_move": None,
        "final_move_uci": None,
        "commentary": "",
        "thought_process": "",
    }

    result = app_agent.invoke(cast("AgentState", initial_state))

    move_uci = result.get("final_move_uci")
    commentary = result.get("commentary", "")

    if not move_uci:
        logger.error("☠️ MAX RETRIES EXCEEDED. Falling back to random.")
        fallback_move = random.choice(list(board.legal_moves))
        move_uci = fallback_move.uci()
        commentary = FALLBACK_COMMENTARY

    return move_uci, commentary
