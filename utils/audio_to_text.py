import os
import uuid

from django.templatetags.i18n import language
from rest_framework.views import APIView
from rest_framework.response import Response
import whisper

model = whisper.load_model("large")
from django.conf import settings

def audio_to_text(audio):
    tmp_dir = os.path.join(settings.MEDIA_ROOT, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.webm"
    file_path = os.path.join(tmp_dir, filename)

    with open(file_path, "wb+") as f:
        for chunk in audio.chunks():
            f.write(chunk)

    try:
        # 4️⃣ Whisper 转文字
        result = model.transcribe(file_path)
        text = result["text"]

    finally:
        # 5️⃣ 用完就删
        if os.path.exists(file_path):
            os.remove(file_path)

    return text

