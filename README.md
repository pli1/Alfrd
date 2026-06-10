# ALFRD — Automated Inventory Management System

ALFRD is a personal IoT project that automates inventory tracking using a Raspberry Pi, a weight sensor, and computer vision. It detects when items are added to or removed from a shelf, identifies what those items are, and logs real-time inventory levels to a cloud database — no manual scanning or counting required.

## Demo

[![ALFRD Demo](https://img.youtube.com/vi/kIcE2fC22lY/0.jpg)](https://www.youtube.com/watch?v=kIcE2fC22lY)

## How It Works

1. **Weight detection** — An HX711 load cell sensor continuously monitors the shelf weight. When a stable change is detected (beyond a noise threshold), it triggers a capture event.
2. **Object recognition** — A camera photo is taken and run through a TensorFlow SSD MobileNet v2 model (90 COCO classes) to identify what items are present.
3. **Inventory update** — Results are uploaded to MongoDB Atlas. Inventory percentage is calculated as `current weight / max recorded weight × 100%` and the catalog is auto-updated.
4. **Visual feedback** — A WS2812 RGB LED strip provides real-time status: white on startup, breathing blue while processing, solid blue on detection complete.

## Tech Stack

| Layer | Technology |
|---|---|
| Hardware | Raspberry Pi, HX711 load cell (GPIO 5/6), PiCamera, WS2812 LED strip (GPIO 18) |
| Object detection | TensorFlow, SSD MobileNet v2 (COCO) |
| Database | MongoDB Atlas |
| Language | Python 3 |
| Libraries | RPi.GPIO, OpenCV, PiCamera, rpi-ws281x, PyMongo, python-dotenv |

## Project Structure

```
alfrd/
├── config.py                       # All constants and env-var loading
├── requirements.txt
├── .env.example                    # Template — copy to .env and fill in secrets
├── .gitignore
│
├── alfrd/                          # Main package
│   ├── main.py                     # Entry point — thin detection loop
│   ├── scale/
│   │   ├── hx711.py                # Low-level HX711 GPIO driver
│   │   └── scale.py                # Spike-filtered weight measurement
│   ├── camera/
│   │   └── camera.py               # PiCamera wrapper
│   ├── detection/
│   │   └── detector.py             # TensorFlow inference (class-based)
│   ├── led/
│   │   └── led.py                  # LED animations and control
│   └── db/
│       └── mongodb.py              # MongoDB schema and inventory logic
│
└── tests/
    ├── test_scale.py
    ├── test_detector.py
    └── test_db.py
```

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/pli1/Alfrd.git
cd Alfrd
pip install -r requirements.txt
```

### 2. Configure secrets

```bash
cp .env.example .env
# Edit .env and set your MongoDB Atlas connection string
```

### 3. Set up the TensorFlow model

Download the SSD MobileNet v2 COCO model and place it at the project root:

```
alfrd/
└── ssdlite_mobilenet_v2_coco_2018_05_09/
    └── frozen_inference_graph.pb
```

Also ensure the TF object-detection `utils/` directory is accessible. Update `TF_RESEARCH_PATH` in `config.py` if needed.

### 4. Calibrate the scale

The reference unit in `config.py` (`SCALE_REFERENCE_UNIT = -441`) is hardware-specific. To recalibrate:

1. Set `SCALE_REFERENCE_UNIT = 1`
2. Record the raw reading with no weight on the scale
3. Place a known weight (e.g. 500g) and record the new reading
4. Set `SCALE_REFERENCE_UNIT = (reading_with_weight - reading_empty) / known_grams`

### 5. Run

```bash
python -m alfrd.main
```

The system calibrates the scale on startup, then continuously monitors the shelf for weight changes.

## Running Tests

```bash
pytest tests/
```

Tests mock all hardware dependencies (RPi.GPIO, PiCamera, rpi-ws281x) so they run on any machine.

## Inventory Logic

- **Inventory %** = `current_weight / max_weight_captured × 100`
- The system learns the "full" weight automatically — the first time an item is placed, it becomes the 100% baseline. If a heavier weight is recorded later, the baseline updates.
- Each detection event is classified as *Added*, *Removed*, or *quantity changed* by diffing the current object list against the previous state.
- All events are timestamped and stored across three MongoDB collections:

| Collection | Contents |
|---|---|
| `status` | Timestamped log of every detection event (weight + objects) |
| `catalog` | Per-item master data: max weight recorded, current inventory % |
| `inventory` | Current items on the shelf with their weights |
