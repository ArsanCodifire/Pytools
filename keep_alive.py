import os
from threading import Thread
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PyTools Status</title>
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: url('https://raw.githubusercontent.com/ArsanCodifire/Profile-pic/refs/heads/main/Bg.jpg') no-repeat center center fixed;
        background-size: cover;
        color: white;
        text-align: center;
        padding-top: 5%;
    }
    img {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: none;
        background: transparent;
    }
    h1 {
        font-size: 2.5em;
        margin-top: 0.5em;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
    }
    p {
        font-size: 1.2em;
        color: #cfcfe8;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.7);
    }
    .status {
        display: inline-block;
        padding: 10px 20px;
        background: rgba(40,167,69,0.9);
        border-radius: 30px;
        font-size: 1em;
        margin-top: 20px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.5);
    }
</style>
</head>
<body>
    <img src="https://raw.githubusercontent.com/ArsanCodifire/Profile-pic/refs/heads/main/PyTools.png" alt="Bot Avatar">
    <h1>🛠️ PyTools Bot</h1>
    <p>All systems operational</p>
    <div class="status">✅ Bot is running 24/7</div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

def run():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

def keep_alive():
    Thread(target=run, daemon=True).start()