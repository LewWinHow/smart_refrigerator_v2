# Smart Refrigerator System

A Django web application for monitoring refrigerator contents, recording food activity, and helping users manage ingredients with AI-powered chat and voice features.

## Features

- **User accounts:** Registration, password login and recovery, user profiles, and face recognition support.
- **Food inventory:** YOLO-based detection of items added to or removed from the refrigerator, with saved images and activity records. Item visibility can be managed with permissions.
- **Monitoring:** A live monitoring page, searchable activity history, and temperature and humidity records when sensor data is supplied.
- **AI assistant:** Chat about available ingredients, recipe ideas, and food storage. The assistant can use refrigerator inventory and supports Chinese and English responses.
- **Voice interaction:** Audio input, speech-to-text, and spoken responses.
- **Notifications:** Email warnings for detected activity and a script for checking near-expiry and expired items.

## Main Components

- `account/`, `user/` — accounts, profiles, and face-related features
- `item/`, `monitoring/` — food detection, inventory permissions, and activity records
- `ai_assistant/` — chat and audio endpoints
- `temperature_and_humidity/` — sensor data and records
- `utils/` — detection, speech, AI, recipe search, and email helpers
- `send_camera_stream.py` — sends camera frames to the Django application
- `real_time_voice_interaction.py` — desktop voice interaction client
- `send_food_expire_email.py` — checks configured shelf-life rules and sends reminders

## Test Account
For local testing:

- Username: `test`
- Password: `(Test123)`
- Upload a clear, front-facing profile photo for the test account to enable face recognition testing.

## Environment Setup

Create and activate an Anaconda environment, then install PyTorch and the GPU version of ONNX Runtime. Choose a PyTorch build compatible with your CUDA setup.

```bash
conda create -n smart-refrigerator python=3.10
conda activate smart-refrigerator
pip install torch torchvision torchaudio
pip install onnxruntime-gpu
```

Before installing InsightFace, install **Microsoft Visual C++ Build Tools** with the C++ build components. Then install InsightFace and Ultralytics manually:

```bash
pip install insightface
pip install ultralytics
```

Install any other Python packages reported as missing in the terminal when you run the feature you need. Voice interaction also requires **FFmpeg**. The LLM assistant requires **Ollama** to be installed and running; the current helper connects to `http://localhost:11434`.

## Run Locally

The project uses SQLite by default. From the project directory, apply database migrations and start the Django server:

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8100
```

Open `http://127.0.0.1:8100/`. The home page redirects to the account login page. For camera monitoring, configure the Django URL in `send_camera_stream.py` and run the script on a device with a camera.

## Configuration Notes

- Place the required YOLO weights in the model directory expected by the detection code. InsightFace may download its model on first use.
- Shelf-life values are configured in `send_food_expire_email.py`; run that script to check items and send email reminders.
- Keep passwords, API credentials, and Django secret keys out of source control. Review Django's debug and host settings before deployment.
![52259221868_b757d6cdea_k.jpg](../52259221868_b757d6cdea_k.jpg)
