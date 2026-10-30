import os
import socket
import base64
from flask import Flask, render_template

app = Flask(__name__)

# 1. Automatically create required directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 2. Automatically generate fallback audio
DEFAULT_AUDIO_B64 = (
    "UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
)

sound_path = "static/sound.mp3"
if not os.path.exists(sound_path):
    with open(sound_path, "wb") as f:
        try:
            f.write(base64.b64decode(DEFAULT_AUDIO_B64))
        except Exception:
            pass

# 3. HTML Content with your exact Merchant Gateway design & audio
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure UPI Gateway</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f2f4f8;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            width: 100%;
            max-width: 380px;
            text-align: center;
        }
        h2 { color: #1a1a1a; margin-bottom: 5px; }
        .amount {
            font-size: 32px;
            font-weight: bold;
            color: #0f766e;
            margin: 15px 0 25px 0;
        }
        .btn {
            background-color: #0f766e;
            color: white;
            border: none;
            padding: 14px 20px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            width: 100%;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background-color: #115e59; }
        .status {
            margin-top: 20px;
            font-weight: 500;
            color: #b91c1c;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <div class="card">
        <p style="color: #666; font-size: 14px; margin:0;">Requesting payment to</p>
        <h2>Merchant Gateway</h2>
        <div class="amount">₹ 500.00</div>
        
        <button class="btn" onclick="triggerPayment()">Pay Now</button>
        <div class="status" id="statusMsg"></div>
    </div>

    <script>
        function triggerPayment() {
            const status = document.getElementById('statusMsg');
            status.innerText = "Processing...";

            const soundUrl = "{{ url_for('static', filename='sound.mp3') }}?t=" + new Date().getTime();
            const audio = new Audio(soundUrl);
            audio.volume = 1.0;

            audio.play().then(() => {
                status.innerText = "🚨 PAYMENT DECLINED! NICE TRY! 😂";
            }).catch(error => {
                console.error("Audio playback error:", error);
                status.innerText = "🚨 DECLINED! (Audio Error: " + error.message + ")";
            });
        }
    </script>
</body>
</html>
"""

with open("templates/pay.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()
PORT = 5000
TARGET_URL = f"http://{LOCAL_IP}:{PORT}/pay"

# Using Google's public API to generate QR code on the fly without needing any local qrcode library!
QR_API_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={TARGET_URL}"

@app.route('/pay')
def pay_screen():
    return render_template('pay.html')

@app.route('/')
def index():
    return f"""
    <div style="text-align: center; font-family: sans-serif; padding-top: 30px;">
        <h2>LAN Payment Prank Server Running!</h2>
        <p>Scan the QR code below:</p>
        <img src="{QR_API_URL}" width="250"><br><br>
        <p>Direct Link: <a href="{TARGET_URL}" target="_blank">{TARGET_URL}</a></p>
    </div>
    """

if __name__ == '__main__':
    print(f"\n[+] Server running at: {TARGET_URL}\n")
    app.run(host='0.0.0.0', port=PORT, debug=True)
