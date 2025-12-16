# ♟️ Neuro-Chess Agents: A Research-Driven Multi-Agent Chess System

> **A Neuro-Symbolic approach to chess engines using LLM Orchestration, LangGraph, and Local Inference (vLLM).**

## 💡 Concept

Unlike traditional engines (Stockfish) that rely on brute-force calculation, **Neuro-Chess Agents** mimics human intuition using Large Language Models, governed by a rigid symbolic validation layer.

This project implements a **Multi-Agent Architecture** to solve the common hallucinations found in LLM chess play. It is based on recent research (2024-2025) suggesting that LLMs perform significantly better with **FEN-state injection**, **Candidate Sampling (Pass@N)**, and **Chain-of-Thought** reasoning.

### 🏗 Architecture

The system is built on **LangGraph** and consists of three specialized agents:

1.  **🧠 The Strategist (LLM):** Analyzes the board (FEN) and proposes strategic candidates using a `Pass@N` sampling method. It operates in a stateless mode to prevent context drift.
2.  **⚖️ The Arbiter (Python Tool):** A symbolic validation layer powered by `python-chess`. It strictly enforces FIDE rules, filtering out "hallucinated" moves from the Strategist.
3.  **🎙️ The Commentator (LLM):** A persona-based agent that narrates the game, reacting to both the board state and the Strategist's "internal monologues" (including failed illegal move attempts).

## 🚀 Tech Stack

*   **Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful Multi-Agent Workflow)
*   **LLM Inference:** Local [vLLM](https://github.com/vllm-project/vllm) / Qwen 2.5 (OpenAI-compatible API)
*   **Chess Logic:** [python-chess](https://python-chess.readthedocs.io/)
*   **Backend:** FastAPI + WebSockets (Real-time bi-directional communication)
*   **Frontend:** HTML5 + Chessboard.js
*   **Package Manager:** uv

## 🛠 Installation & Setup

We use `uv` for blazing fast dependency management.

### 1. Clone the repository
```bash
git clone https://github.com/pueraeternis/neuro-chess-agents.git
cd neuro-chess-agents
```

### 2. Initialize environment
```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Configuration
Create a `.env` file:
```env
# Local vLLM or OpenAI Compatible Endpoint
LLM_BASE_URL="http://localhost:8000/v1"
LLM_API_KEY="sk-fake-key-for-local"
LLM_MODEL="Qwen/Qwen2.5-Coder-32B-Instruct"
```

### 5. Run the Server
```bash
uv run uvicorn src.main:app --reload
```

## 🔬 Research References

This implementation is inspired by:
*   *Zhang et al. (2025)*: "Complete Chess Games Enable LLM Become A Chess Master" — implemented **FEN-based state injection**.
*   *PatientZero (2024)*: "Why LLMs play chess so poorly" — implemented **Stateless interaction** to avoid memory loss.

---
*Built with ❤️ by [pueraeternis](https://github.com/pueraeternis)*
