"""Simple Web Interface for RoboMaster S1.

Run this and open http://localhost:8000 in your browser.
Works with Direct Connection Mode (no App needed).
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import logging

from app.direct_controller import RoboMasterDirectController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RoboMaster S1 Control")
controller = RoboMasterDirectController()

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>RoboMaster S1 Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        h1 { color: #00d4ff; }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .connected { background: #2ecc71; color: white; }
        .disconnected { background: #e74c3c; color: white; }
        button {
            padding: 20px 30px;
            margin: 5px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            background: #00d4ff;
            color: #1a1a2e;
            font-weight: bold;
        }
        button:hover { background: #00a8cc; }
        button:disabled { background: #555; cursor: not-allowed; }
        .controls { margin: 20px 0; }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            max-width: 300px;
            margin: 20px auto;
        }
        .led-colors button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
        }
        .red { background: #e74c3c; }
        .green { background: #2ecc71; }
        .blue { background: #3498db; }
        .yellow { background: #f1c40f; }
        .off { background: #555; }
        pre {
            background: #16213e;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>🤖 RoboMaster S1 Control</h1>
    
    <div id="status" class="status disconnected">
        🔴 Not Connected
    </div>
    
    <div class="controls">
        <h2>Connection</h2>
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
    </div>
    
    <div class="controls">
        <h2>Movement</h2>
        <div class="grid">
            <div></div>
            <button onclick="move('forward')">⬆️ Forward</button>
            <div></div>
            <button onclick="move('left')">⬅️ Left</button>
            <button onclick="stop()">🛑 Stop</button>
            <button onclick="move('right')">➡️ Right</button>
            <div></div>
            <button onclick="move('backward')">⬇️ Back</button>
            <div></div>
        </div>
        <br>
        <button onclick="rotate('cw')">↩️ Rotate CW</button>
        <button onclick="rotate('ccw')">↪️ Rotate CCW</button>
    </div>
    
    <div class="controls">
        <h2>LEDs</h2>
        <div class="led-colors">
            <button class="red" onclick="setLed(255, 0, 0)"></button>
            <button class="green" onclick="setLed(0, 255, 0)"></button>
            <button class="blue" onclick="setLed(0, 0, 255)"></button>
            <button class="yellow" onclick="setLed(255, 255, 0)"></button>
            <button class="off" onclick="setLed(0, 0, 0)">OFF</button>
        </div>
    </div>
    
    <div class="controls">
        <h2>Battery</h2>
        <button onclick="getBattery()">Check Battery</button>
        <span id="battery">--%</span>
    </div>
    
    <div class="controls">
        <h2>Log</h2>
        <pre id="log">Ready...</pre>
    </div>
    
    <script>
        let connected = false;
        
        function log(msg) {
            document.getElementById('log').textContent += '\\n' + msg;
        }
        
        async function connect() {
            try {
                const res = await fetch('/connect', { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    connected = true;
                    document.getElementById('status').className = 'status connected';
                    document.getElementById('status').textContent = '🟢 Connected - ' + data.info;
                    log('Connected: ' + data.info);
                } else {
                    log('Connection failed: ' + data.error);
                }
            } catch (e) {
                log('Error: ' + e);
            }
        }
        
        async function disconnect() {
            try {
                await fetch('/disconnect', { method: 'POST' });
                connected = false;
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('status').textContent = '🔴 Not Connected';
                log('Disconnected');
            } catch (e) {
                log('Error: ' + e);
            }
        }
        
        async function move(direction) {
            if (!connected) { log('Not connected!'); return; }
            try {
                const res = await fetch('/move/' + direction, { method: 'POST' });
                const data = await res.json();
                log('Move: ' + direction + ' - ' + data.status);
            } catch (e) {
                log('Error: ' + e);
            }
        }
        
        async function rotate(direction) {
            if (!connected) { log('Not connected!'); return; }
            try {
                const res = await fetch('/rotate/' + direction, { method: 'POST' });
                const data = await res.json();
                log('Rotate: ' + direction + ' - ' + data.status);
            } catch (e) {
                log('Error: ' + e);
            }
        }
        
        async function stop() {
            if (!connected) { log('Not connected!'); return; }
            try {
                const res = await fetch('/stop', { method: 'POST' });
                const data = await res.json();
                log('Stop: ' + data.status);
            } catch (e) {
                log('Error: ' + e);
            }
        }
        
        async function setLed(r, g, b) {
            if (!connected) { log('Not connected!'); return; }
            try {
                const res = await fetch('/led', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({r, g, b})
                });
                const data = await res.json();
                log('LED: RGB(' + r + ',' + g + ',' + b + ')');
            } catch (e) {
                log('Error: ' + e);
            }
        }
        
        async function getBattery() {
            if (!connected) { log('Not connected!'); return; }
            try {
                const res = await fetch('/battery');
                const data = await res.json();
                document.getElementById('battery').textContent = data.level + '%';
                log('Battery: ' + data.level + '%');
            } catch (e) {
                log('Error: ' + e);
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE


@app.post("/connect")
async def connect():
    try:
        if controller.is_connected:
            return {"success": True, "info": "Already connected"}

        success = controller.connect()
        if success:
            version = controller._robot.get_version()
            return {"success": True, "info": f"v{version}"}
        else:
            return {"success": False, "error": "Connection failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/disconnect")
async def disconnect():
    controller.disconnect()
    return {"status": "disconnected"}


@app.post("/move/{direction}")
async def move(direction: str):
    try:
        if direction == "forward":
            controller.move_forward(0.5, speed=0.3)
        elif direction == "backward":
            controller.move_forward(-0.5, speed=0.3)
        elif direction == "left":
            controller.move(y=0.5, xy_speed=0.3)
        elif direction == "right":
            controller.move(y=-0.5, xy_speed=0.3)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/rotate/{direction}")
async def rotate(direction: str):
    try:
        degrees = 90 if direction == "cw" else -90
        controller.rotate(degrees, speed=50)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/stop")
async def stop():
    try:
        controller.stop()
        return {"status": "stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class LedRequest(BaseModel):
    r: int
    g: int
    b: int


@app.post("/led")
async def set_led(request: LedRequest):
    try:
        effect = (
            "off" if (request.r == 0 and request.g == 0 and request.b == 0) else "on"
        )
        controller.set_led("bottom_all", request.r, request.g, request.b, effect)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/battery")
async def get_battery():
    try:
        level = controller.get_battery()
        return {"level": level}
    except Exception as e:
        return {"level": -1, "error": str(e)}


if __name__ == "__main__":
    print("=" * 50)
    print("RoboMaster S1 Web Interface")
    print("=" * 50)
    print()
    print("Setup:")
    print("1. Set RoboMaster switch to 'Direct Connection'")
    print("2. Connect PC to RoboMaster WiFi")
    print("3. Open http://localhost:8000 in browser")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
