from flask import Flask, request, jsonify
from flask_cors import CORS  # ติดตั้ง flask-cors เพื่อเปิด CORS
from crv import scan_random_ips  # ใช้ฟังก์ชัน scan_random_ips ที่คุณมีอยู่แล้ว

# สร้างแอป Flask
app = Flask(__name__)

# เปิดใช้งาน CORS
CORS(app)  # เปิด CORS เพื่อให้ API สามารถเข้าถึงได้จากเครื่องอื่นในเครือข่าย

PROVIDERS = {
    "True": [(124, 120, 0, 0, 124, 120, 255, 255)],
    "AIS": [(49, 49, 0, 0, 49, 49, 255, 255)],
    "3BB": [(182, 52, 0, 0, 182, 52, 255, 255)],
    "Dtac": [(103, 40, 128, 0, 103, 40, 191, 255)]
}

def identify_provider(ip):
    """
    ตรวจสอบ IP ว่าเป็นของผู้ให้บริการใด
    """
    parts = list(map(int, ip.split('.')))
    for provider, ranges in PROVIDERS.items():
        for r in ranges:
            if (
                r[0] <= parts[0] <= r[4] and
                r[1] <= parts[1] <= r[5] and
                r[2] <= parts[2] <= r[6] and
                r[3] <= parts[3] <= r[7]
            ):
                return provider
    return "Unknown"

@app.route('/scan', methods=['POST'])
def scan_ips():
    data = request.json
    count = data.get('count', 10)
    concurrency = data.get('concurrency', 50)
    timeout = data.get('timeout', 1)

    online_hosts, offline_hosts = scan_random_ips(count, concurrency, timeout)

    # จัดกลุ่มโฮสต์ตามผู้ให้บริการ
    providers = {provider: [] for provider in PROVIDERS}
    providers["Unknown"] = []

    for ip, response_time in online_hosts:
        provider = identify_provider(ip)
        providers[provider].append({'ip': ip, 'response_time': response_time})

    return jsonify({
        "online_hosts": providers,
        "offline_hosts": offline_hosts
    })

if __name__ == '__main__':
    # รัน Flask ด้วยพอร์ตที่ต้องการ (5000)
    app.run(debug=True, host='0.0.0.0', port=5000)