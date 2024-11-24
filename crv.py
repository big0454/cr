import random  
import subprocess  
import concurrent.futures 
import time 

# ช่วง IP ของไทย (ปรับช่วงตามต้องการ)
THAILAND_IP_RANGES = [
    (124, 120, 0, 0, 124, 120, 255, 255),  # True
    (49, 49, 0, 0, 49, 49, 255, 255),      # AIS
    (182, 52, 0, 0, 182, 52, 255, 255),    # 3BB
    (103, 40, 128, 0, 103, 40, 191, 255)   # Dtac
]

def generate_random_ip():
    """
    สุ่ม IP address จากช่วง IP ที่กำหนด
    """
    selected_range = random.choice(THAILAND_IP_RANGES)
    start = selected_range[:4]
    end = selected_range[4:]
    return f"{random.randint(start[0], end[0])}." \
           f"{random.randint(start[1], end[1])}." \
           f"{random.randint(start[2], end[2])}." \
           f"{random.randint(start[3], end[3])}"

def ping_ip(ip, timeout=1):
    """
    Ping IP address และคืนผลลัพธ์ True/False พร้อมเวลา
    """
    try:
        command = ["ping", "-c", "1", "-W", str(timeout), ip]
        start_time = time.time()
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response_time = time.time() - start_time
        return result.returncode == 0, response_time
    except Exception as e:
        return False, 0

def scan_random_ips(count, concurrency=50, timeout=1):
    """
    สแกน IP address แบบสุ่มจากช่วงที่กำหนด
    """
    scanned_ips = set()
    online_hosts = []
    offline_hosts = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for _ in range(count):
            while True:
                ip = generate_random_ip()
                if ip not in scanned_ips:
                    scanned_ips.add(ip)
                    futures.append((executor.submit(ping_ip, ip, timeout), ip))
                    break

        for future, ip in futures:
            try:
                is_online, response_time = future.result()
                if is_online:
                    online_hosts.append((ip, response_time))
                    print(f"{ip} ออนไลน์ (ตอบสนองใน {response_time:.2f} วินาที)")
                else:
                    offline_hosts.append(ip)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดกับ IP {ip}: {e}")

    return online_hosts, offline_hosts

def save_results(online_filename, offline_filename, online_hosts, offline_hosts):
    """
    บันทึกผลลัพธ์แยกไฟล์
    """
    # บันทึกเฉพาะโฮสต์ออนไลน์
    with open(online_filename, 'w') as file:
        for ip, response_time in online_hosts:
            file.write(f"{ip}\n")

    # บันทึกโฮสต์ที่ออฟไลน์ (ถ้าต้องการ)
    with open(offline_filename, 'w') as file:
        for ip in offline_hosts:
            file.write(f"{ip}\n")

def main():
    print("สุ่ม Ping หา IP Address (เฉพาะประเทศไทย)")
    count = int(input("ต้องการสุ่มจำนวนกี่ครั้ง: "))
    concurrency = int(input("จำนวนการทำงานพร้อมกัน (ค่าแนะนำ: 50): "))
    timeout = float(input("ตั้งค่า timeout สำหรับแต่ละ ping (วินาที, ค่าแนะนำ: 1): "))

    print("\nรอสักพักถ้าใช้จำนวนที่เยอะระบบกำลังสแกน...")
    online_hosts, offline_hosts = scan_random_ips(count, concurrency=concurrency, timeout=timeout)

    # บันทึกผลลัพธ์แยกไฟล์
    online_filename = "thvpn.txt"
    offline_filename = "offline_ips.txt"
    save_results(online_filename, offline_filename, online_hosts, offline_hosts)

    print(f"\nสแกนเสร็จสิ้น! บันทึกผลลัพธ์ออนไลน์ในไฟล์: {online_filename}")
    print(f"\nโฮสต์ออนไลน์: {len(online_hosts)} โฮสต์")
    print(f"โฮสต์ที่ออฟไลน์: {len(offline_hosts)} โฮสต์")

    if online_hosts:
        print("\n*** รายชื่อโฮสต์ออนไลน์ ***")
        for ip, response_time in online_hosts:
            print(f"{ip} (ออนไลน์ {response_time:.2f} วินาที)")
    else:
        print("\nไม่มีโฮสต์ออนไลน์ที่พบ")

if __name__ == "__main__":
    main()