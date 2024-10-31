# encoding:UTF-8

import os
import shutil
import re
import time
import sys


def delAll(path):
    """delAll 删除备份文件夹

    Args:
        path (str): 备份文件夹位置
    """
    print("备份文件夹：", path)
    print("是否清空备份文件夹？(yes / no)")
    try:
        s = input("> ")
    except KeyboardInterrupt:
        print("Abort.")
        sys.exit(0)
    if s.lower() in ["yes", "y"]:
        for fileList in os.walk(path):
            for name in fileList[2]:
                os.remove(os.path.join(fileList[0], name))
            shutil.rmtree(path)
        if not os.path.exists(path):
            print("删除成功！")
            print("Abort.")
            time.sleep(1)
            sys.exit(0)
    else:
        print("Abort.")
        sys.exit(0)


def clean(path, backup_path):
    """clean 清理

    Args:
        path (str): 清理目标目录
        backup_path (str): 备份目录
    """
    i = 0
    # 正则表达式
    pattern1 = r".+\.sync-conflict-\S+"
    print("Selected path: " + path)
    # 递归查找目录下文件
    for dirpath, dirs, files in os.walk(path):
        for file in files:
            matchObj1 = re.match(pattern1, file, re.I)
            if matchObj1:
                i += 1
                filePath = os.path.join(dirpath, file)
                print("* {} Found... {}".format(i, filePath))
                if (os.path.exists(backup_path + os.path.sep + file)):
                    try:
                        os.rename(backup_path + os.path.sep + file,
                                  backup_path + os.path.sep + file + str(i))
                    except IOError as err:
                        print("不能重命名" + backup_path + os.path.sep + file, err)
                    try:
                        shutil.move(filePath, backup_path)
                    except IOError as err:
                        print("不能移动" + filePath, err)
                else:
                    try:
                        shutil.move(filePath, backup_path)
                    except IOError as err:
                        print("不能移动" + filePath, err)
    if (i == 0):
        print("\n*No trash file found!")
        print("Abort.")
        time.sleep(1)
        shutil.rmtree(backup_path)
    else:
        if OS_NAME == 'nt':
            os.system("explorer " + backup_path)
        if OS_NAME == 'posix':
            os.system("ls -a " + backup_path)
        delAll(backup_path)


def selectPath() -> str:
    print("====================", "OS:", OS_NAME)
    print("请输入需要处理的目录")
    print("输入 `this` 处理当前目录 ")
    try:
        src = input("=> ")
    except KeyboardInterrupt:
        print("Abort.")
        sys.exit(0)
    if src.lower() == "this" or os.path.exists(src):
        return src
    else:
        raise FileNotFoundError(src)


def mkDir(path):
    """mkDir 创建备份文件夹

    Args:
        path (str): 文件夹路径

    Raises:
        FileNotFoundError: 无法创建文件夹
    """
    if not (os.path.exists(path + os.path.sep + "CLEANED_TEMP_FILES")):
        os.mkdir(path + os.path.sep + "CLEANED_TEMP_FILES")
    time.sleep(0.5)
    if (os.path.exists(path + os.path.sep + "CLEANED_TEMP_FILES")):
        print("备份文件夹创建成功..." + path + os.path.sep + "CLEANED_TEMP_FILES")
        return path + os.path.sep + "CLEANED_TEMP_FILES"
    else:
        raise FileNotFoundError(path + os.path.sep + "CLEANED_TEMP_FILES")


def main():
    """main 主函数，方便外部调用
    """
    # 获取本文件所在目录
    currentPath = os.getcwd() + os.path.sep
    path = selectPath()
    print("备份文件夹目录：（不要在处理的目录下！）")
    try:
        backup_path = input("=> ")
    except KeyboardInterrupt:
        print("Abort.")
        sys.exit(0)

    backup_path = mkDir(backup_path)
    if (path.lower() == "this"):
        clean(currentPath, backup_path)
    else:
        clean(path, backup_path)


OS_NAME = os.name

if __name__ == "__main__":
    if OS_NAME == 'nt':
        os.system('cls')
    elif OS_NAME == 'posix':
        os.system('clear')
    main()
