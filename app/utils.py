import os


def del_file(file_name):
    ''' 删除文件 '''
    if os.path.exists(file_name):
        os.remove(file_name)
