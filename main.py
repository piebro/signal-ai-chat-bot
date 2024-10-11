import json
import websocket
import rel
from config import WS_BASE_URL, SIGNAL_PHONE_NUMBER
from message_handler import process_message


def on_message(ws, message):
    try:
        data = json.loads(message)
        process_message(data)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {message}")
    except Exception as e:
        print(f"Error processing message: {e}")


def on_error(ws, error):
    print(f"WebSocket Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket connection closed: {close_status_code} - {close_msg}")


def on_open(ws):
    print("WebSocket connection opened")


if __name__ == "__main__":
    websocket.enableTrace(False)  # Disable tracing
    ws = websocket.WebSocketApp(
        f"{WS_BASE_URL}/v1/receive/{SIGNAL_PHONE_NUMBER}",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
