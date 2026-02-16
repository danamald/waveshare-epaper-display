[README-epaper.md](https://github.com/user-attachments/files/25351665/README-epaper.md)
# 🖥️ Waveshare e-Paper Display

Display driver and automated image watcher for the Waveshare 7.3" e-Paper HAT (E) on Raspberry Pi Zero 2 W. Receives satellite images and dashboard content from remote nodes and displays them on a 6-color e-Paper screen.

## Hardware

| Component | Model |
|-----------|-------|
| Computer | Raspberry Pi Zero 2 W |
| Display | Waveshare 7.3" e-Paper HAT (E) — 800×480, 6-color |
| Interface | SPI + GPIO (directly mounted on Pi header) |

## Display Specs

- **Resolution:** 800 × 480 pixels
- **Colors:** Black, White, Red, Green, Blue, Yellow (6-color)
- **Refresh time:** ~25 seconds
- **Driver chip:** Uses gpiochip0 on Pi Zero 2 W (no lgpio hacks needed)

## Scripts

### `watch_and_display.py`

Automated watcher daemon that:
1. Polls the SDR node (192.168.1.253) every 30 seconds for new satellite images
2. Monitors the local `~/incoming/` directory for manually pushed images
3. Resizes images to 800×480 to fit the display
4. Drives the e-Paper display using the Waveshare driver

### `display_image.py`

Manual single-image display tool:
```bash
sudo python3 display_image.py /path/to/image.png
```

## Installation

### 1. Enable SPI

```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

### 2. Install Dependencies

```bash
sudo apt install -y python3-pil python3-numpy python3-spidev python3-lgpio sshpass
```

### 3. Install Waveshare Library

```bash
git clone https://github.com/waveshare/e-Paper.git ~/e-Paper
```

### 4. Create Incoming Directory

```bash
mkdir -p ~/incoming
chmod 777 ~/incoming
```

## Usage

### Run the automated watcher
```bash
sudo nohup python3 ~/watch_and_display.py > ~/watcher.log 2>&1 &
```

### Display a single image manually
```bash
sudo python3 ~/display_image.py ~/incoming/satellite_image.png
```

### Monitor the watcher log
```bash
tail -f ~/watcher.log
```

## GPIO Pinout

The e-Paper HAT connects directly to the Pi's 40-pin header:

| e-Paper Pin | GPIO | Function |
|-------------|------|----------|
| RST | GPIO17 | Reset |
| DC | GPIO25 | Data/Command |
| CS | GPIO8 (CE0) | Chip Select |
| BUSY | GPIO24 | Busy signal |
| CLK | GPIO11 (SCLK) | SPI Clock |
| DIN | GPIO10 (MOSI) | SPI Data |

## Notes

- The display **must be driven as root** (sudo) for GPIO access
- Images larger than 800×480 are automatically resized
- The 6-color palette means photos get dithered — satellite imagery looks great
- The Pi Zero 2 W uses **gpiochip0** (unlike the Pi 5 which uses gpiochip4)
- Refresh takes about 25 seconds — the display flashes during update, this is normal

## Part of the Neighborhood Intel Station

This is the display module of the [Neighborhood Intel Station](https://danamald.github.io/neighborhood-intel-station/) — a multi-source RF intelligence dashboard combining NOAA satellite imagery, Ambient Weather data, Meshtastic mesh networking, and RF spectrum monitoring.

## License

MIT
