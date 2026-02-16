import sys, os, time, subprocess
sys.path.append('/home/epaper/e-Paper/RaspberryPi_JetsonNano/python/lib')

from waveshare_epd import epd7in3e
from PIL import Image

WATCH_DIR = '/home/epaper/incoming'
DISPLAYED_FILE = '/home/epaper/.last_displayed'
SDR_HOST = 'sdr@192.168.1.253'
SDR_PASS = '1234'
SDR_PATH = '/home/sdr/noaa_reception/images/'

os.makedirs(WATCH_DIR, exist_ok=True)

def get_last_displayed():
    if os.path.exists(DISPLAYED_FILE):
        with open(DISPLAYED_FILE, 'r') as f:
            return f.read().strip()
    return None

def set_last_displayed(filename):
    with open(DISPLAYED_FILE, 'w') as f:
        f.write(filename)

def file_is_stable(filepath, wait=3):
    size1 = os.path.getsize(filepath)
    time.sleep(wait)
    size2 = os.path.getsize(filepath)
    return size1 == size2 and size2 > 0

def pull_from_sdr():
    try:
        result = subprocess.run(
            ['sshpass', '-p', SDR_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no',
             SDR_HOST, f'ls -t {SDR_PATH}*.png 2>/dev/null | head -1'],
            capture_output=True, text=True, timeout=10
        )
        remote_file = result.stdout.strip()
        if remote_file:
            filename = os.path.basename(remote_file)
            local_path = os.path.join(WATCH_DIR, filename)
            if not os.path.exists(local_path):
                print(f"Pulling new image from SDR: {filename}")
                subprocess.run(
                    ['sshpass', '-p', SDR_PASS, 'scp', '-o', 'StrictHostKeyChecking=no',
                     f'{SDR_HOST}:{remote_file}', local_path],
                    timeout=60
                )
                return True
    except Exception as e:
        print(f"SDR pull error: {e}")
    return False

def display_image(image_path):
    try:
        print(f"New image detected: {image_path}")
        print("Waiting for transfer to complete...")
        if not file_is_stable(image_path):
            time.sleep(5)

        print("Loading image...")
        img = Image.open(image_path)
        img.load()
        img = img.resize((800, 480), Image.LANCZOS)

        print("Initializing e-Paper...")
        epd = epd7in3e.EPD()
        epd.init()

        print("Displaying (15-30 seconds)...")
        epd.display(epd.getbuffer(img))
        time.sleep(5)
        epd.sleep()
        print("Done!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

print("=== Neighborhood Intel Display ===")
print("Watching for new images locally and from SDR node...")

while True:
    pull_from_sdr()

    files = sorted([f for f in os.listdir(WATCH_DIR) if f.endswith(('.png', '.jpg', '.bmp'))])
    if files:
        latest = files[-1]
        if latest != get_last_displayed():
            if display_image(os.path.join(WATCH_DIR, latest)):
                set_last_displayed(latest)
    time.sleep(30)
