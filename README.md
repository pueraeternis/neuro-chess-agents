# ♟️ Neuro-Chess Agents: A Research-Driven Multi-Agent Chess System

> **A Neuro-Symbolic approach to chess engines using LLM Orchestration, LangGraph, and Local Inference.**

![App Screenshot](https://via.placeholder.com/800x400?text=Neuro-Chess+Interface+Screenshot) 
*(Replace this link with a real screenshot of your UI)*

## 💡 Concept

Unlike traditional engines (Stockfish) that rely on brute-force calculation (MiniMax/AlphaBeta), **Neuro-Chess Agents** mimics human intuition using Large Language Models, governed by a rigid symbolic validation layer.

This project implements a **Multi-Agent Architecture** to solve the common hallucinations found in LLM chess play. It is based on recent research (2024-2025) suggesting that LLMs perform significantly better with **FEN-state injection**, **Candidate Sampling**, and **Chain-of-Thought** reasoning.

### 🏗 Architecture

The system is built on **LangGraph** and consists of three specialized agents in a cyclic graph:

1.  **🧠 The Strategist (LLM):** Analyzes the board (FEN) using Chain-of-Thought prompting. It operates in a **stateless mode** to prevent context drift and uses a retry mechanism if moves are illegal.
2.  **⚖️ The Arbiter (Python Tool):** A symbolic validation layer powered by `python-chess`. It strictly enforces FIDE rules, filtering out "hallucinated" moves and providing feedback to the Strategist.
3.  **🎙️ The Commentator (LLM):** A persona-based agent that narrates the game, reacting to both the board state and the Strategist's "internal monologues" (including failed attempts and panic).

## 🧠 Agent Reasoning Example (CoT)

Unlike standard engines, Neuro-Chess explains its logic. Here is a real log from the "Strategist" deciding to play the Sicilian Defense:

```text
INFO | 🧠 STRATEGIST THOUGHTS:
Let's analyze the position step by step.
FEN: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1  

Context: White just played 1.e4.
Candidate moves:
1. ...e5 – mirrors White’s strategy, fights for central control.
2. ...c5 – the Sicilian Defense, asymmetric, fights for initiative.
3. ...e6 – French Defense, solid but blocks the bishop.

Evaluation:
Modern engine analysis evaluates ...c5 and ...e5 as both strong. 
However, ...c5 is often preferred at the highest level because it creates imbalances.
As an engine aiming for a win, I should avoid symmetry.

Therefore, the best move is 1...c5.
```
> **Commentator:** "Ah, c5! Black responds with the Symmetrical Defense—because nothing says 'I respect your e4' like mirroring it with a little sass."

## 🚀 Tech Stack

*   **Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful Multi-Agent Workflow)
*   **LLM Inference:** Local [vLLM](https://github.com/vllm-project/vllm) serving **Qwen 3 235B** (OpenAI-compatible API)
*   **Chess Logic:** [python-chess](https://python-chess.readthedocs.io/)
*   **Backend:** FastAPI + WebSockets (Real-time bi-directional communication)
*   **Frontend:** HTML5 + Chessboard.js (Optimized with Smart Castling & Promotion UI)
*   **DevOps:** Docker & uv

## 🛠 Installation & Setup

### Option A: Docker (Recommended)
Run the full stack with a single command. The container is self-contained (assets included).

1. Create a `.env` file pointing to your LLM provider:
   ```env
   LLM_BASE_URL="http://172.xx.xx.xx:8000/v1"
   LLM_API_KEY="sk-dummy"
   LLM_MODEL="Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
   ```

2. Run:
   ```bash
   docker compose up --build
   ```
3. Open `http://localhost:8000`

---

### Option B: Local Development (uv)

We use `uv` for blazing fast dependency management.

```bash
# 1. Clone
git clone https://github.com/pueraeternis/neuro-chess-agents.git
cd neuro-chess-agents

# 2. Init & Sync
uv venv
source .venv/bin/activate
uv sync

# 3. Download Assets (run once)
uv run download_assets.py

# 4. Run Server
uv run uvicorn src.main:app --reload
```

## 🔬 Research References

This implementation is guided by recent findings in LLM game theory:
*   *Zhang et al. (2025)*: "Complete Chess Games Enable LLM Become A Chess Master" — implemented **FEN-based state injection** and **Pass@N sampling**.
*   *PatientZero (2024)*: "Why LLMs play chess so poorly" — implemented **Stateless interaction** to avoid memory loss and hallucinations.

---
*Built with ❤️ by [pueraeternis](https://github.com/pueraeternis)*