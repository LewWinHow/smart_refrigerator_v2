# Smart Refrigerator System

## 📋 Overview

The Smart Refrigerator System is an intelligent IoT-based solution that combines computer vision, face recognition, and AI-powered assistance to manage refrigerator contents. Built with Django, this system provides real-time monitoring, automatic item detection, expiration tracking, and voice interaction capabilities.

## ✨ Key Features

### 🔐 User Management & Authentication
- **Face Recognition Login**: Secure authentication using facial recognition technology
- **User Profiles**: Complete user management with profile images and personal information
- **IP Security**: Automatic IP blacklisting for suspicious login attempts
- **Password Recovery**: Email-based password reset with verification codes

### 📦 Item Management
- **Automatic Item Detection**: YOLO-based object detection for identifying food items
- **Item Tracking**: Monitor items being added or removed from the refrigerator
- **Expiration Monitoring**: Automatic tracking of item shelf life with email notifications
- **Permission Control**: Private/public item visibility settings

### 🎥 Real-time Monitoring
- **Live Camera Stream**: Continuous monitoring of refrigerator interior
- **Action Detection**: Automatically detect when items are taken out or put in
- **Visual Records**: Capture and store images of all actions with timestamps
- **Temperature & Humidity**: Environmental monitoring (if sensors connected)

### 🤖 AI Assistant
- **Smart Chat Interface**: Conversational AI assistant for recipe recommendations
- **Voice Interaction**: Real-time voice commands and responses
- **Recipe Suggestions**: Get cooking ideas based on available ingredients
- **Storage Tips**: Learn proper storage methods for different foods
- **Multi-language Support**: Responds in the language used by the user

### 📧 Notification System
- **Expiration Alerts**: Email notifications for expiring items
- **Unauthorized Access**: Alerts when items are removed without permission
- **System Warnings**: Important system status updates

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Django 5.2 - Web framework
- SQLite/MySQL - Database
- InsightFace - Face recognition and embedding
- YOLO (Ultralytics) - Object detection
- OpenCV - Image processing
- Whisper - Speech-to-text conversion
- Edge TTS - Text-to-speech synthesis

**AI/ML Models:**
- YOLOv26m - Food item detection
- Buffalo_S - Face analysis and recognition
- GPT/Ollama - Natural language processing
- FunASR/Whisper - Audio transcription

**Frontend:**
- HTML/CSS Templates
- JavaScript for real-time interactions
- Responsive design for multiple devices

### Project Structure

```
smart_refrigerator_v2/
├── account/                 # User authentication and registration
├── ai_assistant/           # AI chat and voice interaction
├── item/                   # Item management and detection
├── login_log/              # Login attempt tracking
├── middleware/             # Custom middleware (IP verification)
├── monitoring/             # Real-time monitoring and recording
├── temperature_and_humidity/ # Environmental sensors
├── user/                   # User profiles and face recognition
├── utils/                  # Utility functions
│   ├── audio_to_text.py    # Speech recognition
│   ├── detect_face.py      # Face detection and matching
│   ├── detect_item.py      # Item detection with YOLO
│   ├── draw_and_save_image.py # Image annotation
│   ├── get_face_embedding.py # Face feature extraction
│   ├── llm.py              # Large language model integration
│   ├── rag.py              # Recipe search engine
│   └── send_email.py       # Email notification system
├── templates/              # HTML templates
├── media/                  # Uploaded files and images
├── ai_model/yolo_model/    # Pre-trained YOLO models
├── static/                 # Static files (CSS, JS)
├── manage.py               # Django management script
├── send_camera_stream.py   # Camera streaming client
├── send_command.py         # Raspberry Pi control interface
├── real_time_voice_interaction.py # Voice interaction system
└── send_food_expire_email.py # Expiration notification scheduler
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- CUDA-enabled GPU (recommended for better performance)
- FFmpeg (for audio conversion)
- Webcam or camera module
- MySQL (optional, SQLite is default)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd smart_refrigerator_v2
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install django
pip install pillow
pip install opencv-python
pip install ultralytics
pip install insightface
pip install numpy
pip install requests
pip install whisper
pip install edge-tts
pip install simpleaudio
pip install sounddevice
pip install scipy
pip install ddgs
pip install user-agents
pip install jupyter-core
pip install djangorestframework
```

### Step 4: Configure Database

The project uses SQLite by default. To use MySQL:

1. Uncomment the MySQL configuration in `smart_refrigerator_v2/settings.py`
2. Update database credentials
3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Configure Email Settings

Update email configuration in `smart_refrigerator_v2/settings.py`:

```python
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
```

### Step 6: Download AI Models

Place the YOLO model in `ai_model/yolo_model/`:
- `yolo26m.pt` (included in repository)

InsightFace models will be downloaded automatically on first run.

### Step 7: Run the Server

```bash
python manage.py runserver 0.0.0.0:8100
```

Access the application at: `http://localhost:8100`

## 🔧 Configuration

### Camera Setup

For local testing, use `send_camera_stream.py`:

```python
# Update DJANGO_URL if needed
DJANGO_URL = "http://127.0.0.1:8100/item/receive_and_detect_image/"
```

Run the camera stream:
```bash
python send_camera_stream.py
```

### Raspberry Pi Integration

For hardware deployment on Raspberry Pi:

1. Update `send_command.py` with your Pi's IP address:
```python
FLASK_URL = "http://YOUR_PI_IP:5005/receive"
```

2. The system can control fans and other peripherals based on item detection.

### Voice Interaction

Start the voice interaction system:
```bash
python real_time_voice_interaction.py
```

This enables:
- Real-time speech recognition
- AI-powered responses
- Text-to-speech output

## 📱 Usage Guide

### 1. User Registration

1. Navigate to `/account/register/`
2. Fill in user details (username, password, email, etc.)
3. Upload a clear profile photo for face recognition
4. Submit the form

### 2. Login

**Option A: Traditional Login**
- Enter username and password at `/account/login/`

**Option B: Face Recognition**
- System automatically detects faces via camera
- Matches against registered face embeddings

**Supervisor Account (Admin Access)**
- Username: `lewwinhow`
- Password: `(XiaoHao6070)`
- This account has full administrative privileges
- Can access Django admin panel at `/admin/`
- Can manage all users, items, and system settings

### 3. Item Management

Items are automatically detected when:
- Camera stream is active
- Items are placed in/removed from refrigerator
- System records action with timestamp and image

View items at: `/item/`

### 4. AI Assistant

Access the chat interface at: `/ai_assistant/chat/`

**Available Commands:**
- "What's in the fridge?" - List current items
- "Recipe for [ingredient]" - Get cooking suggestions
- "How to store [food]?" - Storage tips
- General questions about food and cooking

**Voice Mode:**
- Speak naturally to interact
- System responds with voice and text

### 5. Monitoring Dashboard

View real-time monitoring at: `/monitoring/`

Features:
- Live camera feed
- Recent activity log
- Detected items visualization
- Action history (put in/take out)

### 6. Expiration Notifications

The system automatically:
- Tracks item age based on predefined shelf lives
- Sends email alerts 3 days before expiration
- Notifies immediately when items expire

Customize expiration periods in `send_food_expire_email.py`:

```python
EXPIRATION_DAYS = {
    'apple': 14,
    'banana': 3,
    'chicken': 0,
    # Add more items...
}
```

## 🔒 Security Features

### IP Blacklisting
- Automatically blocks IPs after 5 failed login attempts
- Bot detection and prevention
- Configurable in `middleware/verify_ip_middleware.py`

### Password Requirements
- Minimum 8 characters
- Must contain uppercase, lowercase, numbers, and special characters
- Maximum 128 characters

### Session Management
- 24-hour session timeout
- Secure cookie handling
- CSRF protection enabled

## 🛠️ API Endpoints

### Authentication
- `POST /account/login/` - User login
- `POST /account/register/` - User registration
- `GET /account/logout/` - User logout
- `POST /account/forgot_password/` - Password recovery

### Items
- `POST /item/receive_and_detect_image/` - Process camera image
- `GET /item/list/` - List all items
- `POST /item/add/` - Manually add item

### AI Assistant
- `POST /ai_assistant/receive_message_and_use_llm/` - Send chat message
- `POST /ai_assistant/receive_audio_and_convert_to_text/` - Speech-to-text
- `POST /ai_assistant/receive_audio_and_response/` - Voice interaction
- `GET /ai_assistant/get_chat/` - Retrieve chat history

### Monitoring
- `GET /monitoring/get_monitoring_display_and_detect_data/` - Get monitoring data
- `POST /monitoring/capture/` - Trigger camera capture

## 📊 Database Schema

### Core Tables

**user**
- Standard Django auth fields
- birthday, gender, phone
- profile_image, update_time

**face_id**
- user (FK)
- embedding (BinaryField - pickle serialized)

**item**
- item (name)
- user (owner)
- image
- permissions (0=private, 1=public)
- record_time

**monitoring_record**
- item (detected item name)
- user (who performed action)
- action (0=take out, 1=put in)
- image (captured frame)
- record_time

**chat**
- user (FK)
- message (text)
- sender (1=user, 2=system)

## 🧪 Testing

Run Django tests:
```bash
python manage.py test
```

Test specific modules:
```bash
python manage.py test item
python manage.py test ai_assistant
```

## 🐛 Troubleshooting

### Common Issues

**1. Face Recognition Not Working**
- Ensure webcam is accessible
- Check InsightFace model download
- Verify good lighting conditions
- Use clear, front-facing profile photos

**2. Item Detection Failures**
- Verify YOLO model exists in `ai_model/yolo_model/`
- Check camera resolution and angle
- Ensure items are within allowed classes (fruits, vegetables, etc.)
- Review detection confidence threshold (default: 0.5)

**3. Email Notifications Not Sending**
- Verify Gmail app password (not regular password)
- Check EMAIL_HOST settings
- Ensure less secure apps access is enabled (or use App Passwords)

**4. Voice Interaction Issues**
- Install FFmpeg: `sudo apt install ffmpeg` (Linux) or download for Windows
- Check microphone index in `real_time_voice_interaction.py`
- Verify audio device permissions

**5. Database Errors**
- Run migrations: `python manage.py migrate`
- Check database connection settings
- For MySQL: ensure service is running

### Performance Optimization

**GPU Acceleration:**
- Install CUDA and cuDNN
- Set `ctx_id=0` in face detection code
- YOLO automatically uses GPU if available

**Database Optimization:**
- Switch to MySQL for production
- Enable connection pooling
- Add database indexes for frequently queried fields

## 📝 Development Notes

### Customizing AI Responses

Modify prompts in `utils/llm.py` to change assistant behavior.

### Adding Expiration Periods

Update `EXPIRATION_DAYS` dictionary in `send_food_expire_email.py`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is proprietary. All rights reserved.

## 👥 Credits

Developed for NEIVCE (New Era Vocational College of Education) Smart Refrigerator Project.

**Key Technologies:**
- Django Web Framework
- InsightFace for facial recognition
- Ultralytics YOLO for object detection
- OpenAI/Ollama for language processing
- Edge TTS for speech synthesis

## 📞 Support

For issues or questions:
- Email: xiaohao6070@gmail.com
- Check the troubleshooting section above
- Review Django documentation: https://docs.djangoproject.com/

## 🔄 Future Enhancements

Potential improvements:
- Mobile app integration
- Barcode scanning for packaged items
- Nutritional information tracking
- Meal planning suggestions
- Shopping list generation
- Multi-refrigerator support
- Advanced analytics dashboard
- Integration with smart home systems

---

**Version:** 2.0  
**Last Updated:** 2026  
**Framework:** Django 5.2  
**Python:** 3.8+
