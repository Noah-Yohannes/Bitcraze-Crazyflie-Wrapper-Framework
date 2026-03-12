import websocket
import threading
import sys
import time 

def on_message(ws, message):
    print(f"Received from server: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    time.sleep(5)
    print("Connection closed")

def on_open(ws):
    def run(*args):
        while True:
            # message = input("Enter message to send: ")
            message =  """{"positions":[{"x":0.00999999978,"y":0.994000018,"z":-0.128000006},{"x":-0.209999993,"y":0.994000018,"z":0.0260000005},
        {"x":-0.0980000049,"y":0.994000018,"z":0.203999996},{"x":0.0889999941,"y":0.994000018,"z":0.194000006},
        {"x":0.213999987,"y":0.994000018,"z":0.00400000019}]}"""
            message = """{"positions":[
            {"x":0.00999999978,"y":0.3094000018,"z":-0.128000006},
            {"x":0.209999993,"y":0.3094000018,"z":0.0260000005},
            {"x":0.4080000049,"y":0.554000018,"z":0.203999996},
            {"x":0.6089999941,"y":0.884000018,"z":0.194000006},
            {"x":0.753999987,"y":0.554000018,"z":0.00400000019}]}"""
            ws.send(message)
    threading.Thread(target=run).start()

if __name__ == "__main__":
    default_url = "ws://localhost:8765"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()