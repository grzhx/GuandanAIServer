"""
Guandan AI Server
Provides HTTP endpoint with WebSocket interface for AI card playing
"""

import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn

from game.card import Card, parse_cards, cards_to_dict_list
from ai import create_ai, AIConfig

# Configure logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Guandan AI Server",
    description="AI server for Guandan (掼蛋) card game",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Guandan AI Server is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for AI game interaction
    
    Receives messages in format:
    {
        "msg": "ai_call",
        "level": <level_card_number>,
        "last_move": [{"color": "...", "number": ...}, ...],
        "your_cards": [{"color": "...", "number": ...}, ...]
    }
    
    Responds with:
    {
        "action": "play_cards",
        "cards": [{"color": "...", "number": ...}, ...]
    }
    or
    {
        "action": "pass"
    }
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            
            try:
                message = json.loads(data)
                
                # Validate message format
                if message.get("msg") != "ai_call":
                    await websocket.send_json({
                        "error": "Invalid message type, expected 'ai_call'"
                    })
                    continue
                
                # Extract request_id and game state
                request_id = message.get("request_id")
                level = message.get("level", 2)
                last_move_data = message.get("last_move", [])
                your_cards_data = message.get("your_cards", [])
                
                # Parse cards
                last_move = parse_cards(last_move_data) if last_move_data else []
                hand = parse_cards(your_cards_data)
                
                logger.info(f"Level: {level}, Last move: {len(last_move)} cards, Hand: {len(hand)} cards")
                
                # Create AI and find best play
                ai = create_ai(level)
                play = ai.find_best_play(hand, last_move)
                
                # Prepare response (empty cards list means pass)
                response = {
                    "action": "play_cards",
                    "cards": cards_to_dict_list(play) if play else []
                }
                
                # Include request_id if provided
                if request_id is not None:
                    response["request_id"] = request_id
                
                logger.info(f"Response: {response}")
                await websocket.send_json(response)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await websocket.send_json({
                    "error": f"Invalid JSON: {str(e)}"
                })
            except KeyError as e:
                logger.error(f"Missing key: {e}")
                await websocket.send_json({
                    "error": f"Missing required field: {str(e)}"
                })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({
                    "error": f"Processing error: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
