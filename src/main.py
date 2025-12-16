import json

import chess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.agent import get_agent_move
from src.config import (
    APP_TITLE,
    INDEX_HTML_PATH,
    STATIC_DIR,
    STATIC_URL_PREFIX,
    UVICORN_HOST,
    UVICORN_PORT,
)
from src.logger import logger

app = FastAPI(title=APP_TITLE)
app.mount(
    STATIC_URL_PREFIX,
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


@app.get("/")
async def read_root():
    return FileResponse(str(INDEX_HTML_PATH))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected")

    board = chess.Board()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "human_move":
                move_uci = message.get("move_uci")
                logger.info(f"Received move: {move_uci}")

                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        logger.warning(f"Illegal move attempted: {move_uci}")
                        await websocket.send_json(
                            {
                                "action": "update_board",
                                "fen": board.fen(),
                            },
                        )
                        continue
                except ValueError:
                    continue

                if not board.is_game_over():
                    logger.info("Agent is thinking...")

                    ai_move_uci, commentary = get_agent_move(board)

                    ai_move = chess.Move.from_uci(ai_move_uci)
                    board.push(ai_move)

                    logger.info(f"AI moved: {ai_move_uci} | Comment: {commentary}")

                    await websocket.send_json(
                        {
                            "action": "update_board",
                            "fen": board.fen(),
                            "last_move": ai_move.uci(),
                            "commentary": commentary,
                        },
                    )

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

    uvicorn.run(app, host=UVICORN_HOST, port=UVICORN_PORT)
