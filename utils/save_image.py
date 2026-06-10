import os
import uuid
from django.core.files.storage import FileSystemStorage
from smart_refrigerator_v2 import settings

def save_image(image_file, sub_folder='uploads'):
    """
    Save uploaded image to MEDIA_ROOT/sub_folder/
    Returns relative path (relative to MEDIA_ROOT), used for ImageField or database storage
    """
    # Save directory
    save_dir = os.path.join(settings.MEDIA_ROOT, sub_folder)
    os.makedirs(save_dir, exist_ok=True)

    # Get extension
    ext = os.path.splitext(image_file.name)[1]  # Use .name to get filename
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Save file
    fs = FileSystemStorage(location=save_dir)
    fs.save(unique_filename, image_file)

    # Return relative path (relative to MEDIA_ROOT)
    return os.path.join(sub_folder, unique_filename).replace("\\", "/")
