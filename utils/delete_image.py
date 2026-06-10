import os
from django.conf import settings

def delete_single_image(filename, sub_folder='media'):
    """
    Delete image with specified filename in media/sub_folder/
    :param filename: Filename to delete (e.g., 'abc123.jpg')
    :param sub_folder: Subpath relative to media (e.g., 'display_detect')
    :return: True if deleted successfully, False otherwise
    """
    # Build full path
    file_path = os.path.join(settings.MEDIA_ROOT, sub_folder, filename)

    # Security check
    if '..' in filename or '/' in filename or '\\' in filename:
        print("Illegal filename")
        return False

    # Check and delete
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            os.remove(file_path)
            # print(f"File deleted: {file_path}")
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
    else:
        print("File does not exist")
        return False

import os
from django.conf import settings

def delete_all_images(sub_folder='monitoring_display'):
    """
    Delete all files in media/sub_folder/ (do not delete the folder itself)
    :param sub_folder: Subpath relative to media
    :return: True on success, False on failure
    """
    folder_path = os.path.join(settings.MEDIA_ROOT, sub_folder)

    if not os.path.exists(folder_path):
        print("Path does not exist:", folder_path)
        return False

    success = True
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                # print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Delete failed: {file_path}, Error: {e}")
                success = False
    return success
