import uuid

from django.core.files.storage import FileSystemStorage

def save_profile_image(profile_image, folder):
    fs = FileSystemStorage(location='media/profile_image', base_url='/media/profile_image/')
    ext = profile_image.name.split('.')[-1]
    new_image_name = f"{uuid.uuid4()}.{ext}"
    image_path = f"{folder}/{fs.save(new_image_name, profile_image)}"
    return image_path