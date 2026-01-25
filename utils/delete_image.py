import os
from django.conf import settings

def delete_single_image(filename, sub_folder='media'):
    """
    删除 media/sub_folder/ 下指定文件名的图像
    :param filename: 要删除的文件名（如 'abc123.jpg'）
    :param sub_folder: 相对于 media 的子路径（如 'display_detect'）
    :return: True 删除成功，False 删除失败
    """
    # 构建完整路径
    file_path = os.path.join(settings.MEDIA_ROOT, sub_folder, filename)

    # 安全检查
    if '..' in filename or '/' in filename or '\\' in filename:
        print("非法文件名")
        return False

    # 判断并删除
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            os.remove(file_path)
            # print(f"已删除文件：{file_path}")
            return True
        except Exception as e:
            print(f"删除失败：{e}")
            return False
    else:
        print("文件不存在")
        return False

import os
from django.conf import settings

def delete_all_images(sub_folder='monitoring_display'):
    """
    删除 media/sub_folder/ 下的所有文件（不删除文件夹本身）
    :param sub_folder: 相对于 media 的子路径
    :return: 成功返回 True，失败返回 False
    """
    folder_path = os.path.join(settings.MEDIA_ROOT, sub_folder)

    if not os.path.exists(folder_path):
        print("路径不存在：", folder_path)
        return False

    success = True
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                # print(f"已删除：{file_path}")
            except Exception as e:
                print(f"删除失败：{file_path}, 错误：{e}")
                success = False
    return success
