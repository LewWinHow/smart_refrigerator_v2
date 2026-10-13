import os
import uuid

from django.conf import settings
import whisper

# ✅ Load Whisper small model (ultra-small & fast)
model = whisper.load_model("tiny")


def audio_to_text(audio):
    tmp_dir = os.path.join(settings.MEDIA_ROOT, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.webm"
    file_path = os.path.join(tmp_dir, filename)

    # Save uploaded audio
    with open(file_path, "wb+") as f:
        for chunk in audio.chunks():
            f.write(chunk)

    try:
        # ✅ Whisper recognition (automatically handles format)
        result = model.transcribe(file_path)

        text = result["text"]

    finally:
        # Delete temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

    return text