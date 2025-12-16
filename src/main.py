import json

import chess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.agent import get_agent_move
from src.logger import logger

app = FastAPI(title="Neuro-Chess Agents")

# Подключаем статику (наш фронтенд)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected")

    # Инициализируем новую игру для этого соединения
    board = chess.Board()

    try:
        while True:
            # Ждем сообщение от клиента
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "human_move":
                move_uci = message.get("move_uci")
                logger.info(f"Received move: {move_uci}")

                # 1. Применяем ход игрока (Server Authoritative)
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        logger.warning(f"Illegal move attempted: {move_uci}")
                        # Возвращаем текущее состояние (откат на клиенте)
                        await websocket.send_json(
                            {
                                "action": "update_board",
                                "fen": board.fen(),
                            },
                        )
                        continue
                except ValueError:
                    continue

                # 2. Ход "Агента" (Neuro-Symbolic Agent)
                if not board.is_game_over():
                    logger.info("Agent is thinking...")

                    # --- Вызов LangGraph Agent ---
                    ai_move_uci, commentary = get_agent_move(board)
                    # -----------------------------

                    # Применяем ход
                    ai_move = chess.Move.from_uci(ai_move_uci)
                    board.push(ai_move)

                    logger.info(f"AI moved: {ai_move_uci} | Comment: {commentary}")

                    # Отправляем клиенту
                    await websocket.send_json(
                        {
                            "action": "update_board",
                            "fen": board.fen(),
                            "last_move": ai_move.uci(),
                            "commentary": commentary,  # Передаем комментарий на фронт!
                        },
                    )

                # 3. Отправляем обновленное состояние клиенту
                await websocket.send_json(
                    {
                        "action": "update_board",
                        "fen": board.fen(),
                        "last_move": ai_move.uci() if "ai_move" in locals() else None,
                    },
                )

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
