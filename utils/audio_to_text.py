# import os
# import uuid
#
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.conf import settings
#
# from funasr import AutoModel
#
# # ✅ Load model (Chinese optimized)
# # model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc-c"
# model = AutoModel(
#     model="paraformer-en-small",
#     vad_model="fsmn-vad",
#     punc_model="ct-punc-c"
# )
#
# def audio_to_text(audio):
#     tmp_dir = os.path.join(settings.MEDIA_ROOT, "tmp")
#     os.makedirs(tmp_dir, exist_ok=True)
#
#     filename = f"{uuid.uuid4()}.webm"
#     file_path = os.path.join(tmp_dir, filename)
#
#     # Save uploaded audio
#     with open(file_path, "wb+") as f:
#         for chunk in audio.chunks():
#             f.write(chunk)
#
#     try:
#         # ✅ FunASR recognition
#         res = model.generate(input=file_path)
#
#         # ⚠️ FunASR returns a list
#         text = res[0]["text"]
#
#     finally:
#         # Delete temporary file
#         if os.path.exists(file_path):
#             os.remove(file_path)
#
#     return text
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