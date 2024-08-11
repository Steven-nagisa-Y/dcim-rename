# coding=utf-8

import os
import re
from sys import exit
from typing import List, Optional, Tuple, Dict
from tinydb import TinyDB, Query
import exifread


DB_NAME = ''
PATH = ''
SAVED_DB = 'SAVED_PREFERENCE'

def read_preference() -> Tuple[Optional[str], Optional[str]]:
    """
    读取用户偏好信息
    
    Args:
        无参数
    
    Returns:
        Tuple[Optional[str], Optional[str]]: 包含两个元素的元组，分别表示数据库名称和数据库路径。
            如果读取失败或用户未选择任何偏好信息，则返回两个None。
    
    """
    db_file = f"./Database/{SAVED_DB}.json"
    if not os.path.exists(db_file):
        return None, None
    db = TinyDB(db_file)
    all_pref = db.all()
    if 0 == len(all_pref):
        # 数据库为空
        return None, None
    print('已保存的数据库路径：\n（输入编号选择现有，输入del<序号>删除）')
    i = 0
    for line in all_pref:
        print(f'{i}. {line["db_name"]}：{line["path"]}')
        i += 1
    try:
        select = input('> ')
    except KeyboardInterrupt:
        exit("User type exit")
    except EOFError:
        exit("User type exit")
    if (select.startswith('del')):
        # 删除
        select = select.replace('del', '').strip()
        if not select.isdigit():
            print("输入错误！")
            return read_preference()
        else:
            select = int(select)
        if select >= i:
            print("输入错误！")
            return read_preference()
        else:
            db.remove(Query().path == all_pref[select]['path'])
            print(f'已删除{all_pref[select]["db_name"]}：{all_pref[select]["path"]}')
            return read_preference()
    else:
        # 读取
        select = select.strip()
        if select == '':
            # 跳过读取已有
            return None, None
        if not select.isdigit() or int(select) >= i:
            print("输入错误！")
            return read_preference()
        select = int(select)
        # 读取已有
        return all_pref[select]['db_name'], all_pref[select]['path']

def write_preference(db_name, path) -> List:
    """
    将偏好信息写入数据库
    
    Args:
        db_name (str): 数据库名称
        path (str): 数据库文件路径
    
    Returns:
        list: 数据库中的所有记录
    
    """
    db_file = f"./Database/{SAVED_DB}.json"
    if not os.path.exists(db_file):
        db = create_db(SAVED_DB)
    else:
        db = TinyDB(db_file)
    exist = db.get(Query().db_name == db_name)
    if exist:
        print(f'{db_name}已存在，将覆盖原路径！')
        db.update({'path': path}, Query().db_name == db_name)
    else:
        print(f'{db_name}已保存！')
        db.insert({'db_name': db_name, 'path': path})
    return db.all()

def select_path() -> str:
    """
    选择需要处理的目录
    
    Args:
        无参数
    
    Returns:
        str: 返回所选目录的路径字符串，若路径无效则返回字符串 "err"
    
    """
    print("===========================================================")
    print("请输入需要处理的目录，例如：/DCIM/Camera ")
    print("输入 DCIM 处理当前目录下图片 ")
    try:
        src = input("> ")
    except KeyboardInterrupt:
        quit("User type exit")
    if src.lower() == 'dcim':
        _path = os.getcwd() + os.path.sep + 'DCIM'
    else:
        _path = src
    if not os.path.exists(_path):
        print("路径无效！")
        return "err"
    return _path


def create_db(db_name=None) -> TinyDB:
    """
    创建一个新的TinyDB数据库并返回该数据库实例。
    
    Args:
        db_name (str, optional): 数据库名称。如果未提供，则使用默认值 'photo_db'。
    
    Returns:
        TinyDB: 创建的数据库实例。
    
    """
    if not db_name:
        db_name = 'photo_db'
    global DB_NAME
    DB_NAME = db_name
    db_name = f"./Database/{db_name}.json"
    if os.path.exists(db_name):
        os.remove(db_name)
    db = TinyDB(db_name)
    return db


def db_set(db, path, ori, new, status='GOOD') -> List[Dict]:
    """
    向数据库插入一条记录，并返回所有记录。
    
    Args:
        db (object): 数据库对象。
        path (str): 文件路径。
        ori (str): 原始文件路径
        new (str): 新文件路径
        status (str, optional): 状态，默认为'GOOD'。
    
    Returns:
        List[Dict]: 所有记录的列表，每个记录是一个字典，包含'path'、'original'、'new'和'status'四个键。
    
    """
    ori = str(ori)
    new = str(new)
    db.insert({'path': path, 'original': ori, 'new': new, 'status': status})
    return db.all()


def db_get(db, query, value):
    """
    从数据库中获取与给定查询和值匹配的记录。
    
    Args:
        db: 数据库对象，用于执行查询操作。
        query: 查询语句，用于匹配数据库中的记录。
        value: 查询值，用于匹配数据库中的记录。
    
    Returns:
        返回与给定查询和值匹配的数据库记录列表。
    
    """
    return db.search(query == value)


def do_rename(dirname, file, db, i, t=None, msg=None):
    match_name = re.match(r'^(?P<name>[\S\s]+)\.(?P<ext>\S+)$', file)
    file_name = match_name.groupdict()['name']
    file_ext = match_name.groupdict()['ext']
    file_ext = file_ext.lower()
    if file_ext == 'jpeg':
        file_ext = 'jpg'
    if i == 0 and t != None:
        # 通过EXIF更改图片文件名
        from time import strptime, strftime
        file_time = strptime(t, "%Y:%m:%d %H:%M:%S")
        file_name = strftime("%Y%m%d_%H%M%S", file_time)
        ori_name = file
        new_name = "IMG_" + file_name + "." + file_ext
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 1:
        # 通过时间戳文件名修改
        from time import localtime, strftime
        Photo = Query()
        time_stamp = int(file_name)
        # 尝试10次重命名
        for _ in range(10):
            time_local = localtime(time_stamp/1000)
            file_name_formatted = strftime("%Y%m%d_%H%M%S", time_local)
            new_name = "IMG_" + file_name_formatted + "." + file_ext
            db_value = db_get(db, Photo.new, new_name)
            if db_value:
                time_stamp += 1000
            else:
                break
        ori_name = file
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 2:
        # 修改傻逼微信QQ保存的图片文件名
        from time import localtime, strftime
        Photo = Query()
        try:
            time_stamp = int(
                file_name
                    .replace('mmexport', '')
                    .replace('microMsg.', '')
                    .replace('Image_', '')
            )
        except ValueError:
            print(f'{file_name} is not a valid file name.')
            return "err"
        # 尝试60次重命名
        for _ in range(60):
            time_local = localtime(time_stamp/1000)
            file_name_formatted = strftime("%Y%m%d_%H%M%S", time_local)
            new_name = "IMG_" + file_name_formatted + "." + file_ext
            db_value = db_get(db, Photo.new, new_name)
            if db_value:
                time_stamp += 1000
            else:
                break
        ori_name = file
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 3:
        # 没有IMG标识头，添加标识头
        ori_name = file
        new_name = 'IMG_' + ori_name
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 4:
        from time import strptime, strftime
        file_time = strptime(file_name, "%Y-%m-%d %H.%M.%S")
        file_name = strftime("%Y%m%d_%H%M%S", file_time)
        ori_name = file
        new_name = "IMG_" + file_name + "." + file_ext
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 10:
        # 直接重新格式化文件名
        ori_name = file
        file_name = file_name[0:3] + '_' + \
            file_name[3:11] + '_' + file_name[11:]
        new_name = file_name + "." + file_ext
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 11:
        # 删除多余部分
        ori_name = file
        file_name = file_name[:19]
        new_name = file_name + "." + file_ext
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == 12:
        # 没有VID标识头，添加标识头
        ori_name = file
        new_name = 'VID_' + ori_name[6:]
        db_set(db, dirname, ori_name, new_name)
        return "ok"
    if i == -1:
        if msg:
            # 无法自动重命名
            msg = msg.replace('\n', '')
            db_set(db, dirname, file, msg, status='ERROR')
            return "ok"
        else:
            return "err"


def quit(errMsg=None):
    if not errMsg == None:
        print(
            f'[EXIT] Because of {errMsg} Program aborted.')
        exit(1)
    else:
        print(f'[INFO] 程序正常退出。')
        exit(0)


def main() -> str:
    """
    对指定路径下的图片和视频进行重命名，并统计各类文件数量。
    
    Args:
        无
    
    Returns:
        str: 返回一个字符串，表示执行结果。
    
    """
    pref = read_preference()
    if pref is not None:
        db_name, path = pref
    if path is None:
        path = select_path()
        if path == "err":
            return "Selected path is not exist"
    print("输入数据库文件名")
    if db_name is None:
        try:
            db_name = input('(Default) photo_db > ')
        except KeyboardInterrupt:
            return "Input Database name error"
        except ValueError:
            return "Input Database value error"
    db = create_db(db_name)
    global DB_NAME, PATH
    DB_NAME = db_name
    PATH = path
    count = {
        'all': 0,
        'good': 0,
        'dismatch': 0,
        'video': 0
    }
    img_pattern = r'.+\.(jpg|jpeg|heic|png)'
    vid_pattern = r'.+\.(mp4|mov|3gp)'
    for dirpath, _, files in os.walk(path):
        for file in files:
            count['all'] += 1
            match_img = re.match(img_pattern, file, re.I)
            match_vid = re.match(vid_pattern, file, re.I)
            if match_img:
                good_img_pattern = r'((IMG|PANO|Screenshot|PXL)_\d{8}_\d{6}(_HDR)?(_\w+\.\w+\..+)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG))'
                next1_img_pattern = r'\d{13}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                next2_img_pattern = r'IMG_\d{8}_\d{6}.+\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                next3_img_pattern = r'IMG\d{14}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                next4_img_pattern = r'(mmexport|microMsg\.|Image_)\d{13}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                next5_img_pattern = r'\d{8}_\d{6}(_HDR)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                next6_img_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}\.\d{2}\.\d{2}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                if re.match(good_img_pattern, file):
                    print(f"[ OK ] {file}")
                    count['good'] += 1
                elif re.match(next1_img_pattern, file):
                    print(f"[INFO] Match timestamp {file}")
                    do_rename(dirpath, file, db, 1)
                    count['dismatch'] += 1
                elif re.match(next2_img_pattern, file):
                    print(f"[INFO] Match extra text {file}")
                    do_rename(dirpath, file, db, 11)
                    count['dismatch'] += 1
                elif re.match(next3_img_pattern, file):
                    print(f"[INFO] Match missing underline {file}")
                    do_rename(dirpath, file, db, 10)
                    count['dismatch'] += 1
                elif re.match(next4_img_pattern, file):
                    print(f"[INFO] Match WX timestamp {file}")
                    do_rename(dirpath, file, db, 2)
                    count['dismatch'] += 1
                elif re.match(next5_img_pattern, file):
                    print(f"[INFO] Match Head missing {file}")
                    do_rename(dirpath, file, db, 3)
                    count['dismatch'] += 1
                elif re.match(next6_img_pattern, file):
                    print(f"[INFO] Match New Format {file}")
                    do_rename(dirpath, file, db, 4)
                    count['dismatch'] += 1
                else:
                    count['dismatch'] += 1
                    try:
                        f = open(dirpath + os.path.sep + file, 'rb')
                        exif_tags = exifread.process_file(f)
                        f.close()
                    except PermissionError:
                        return "File access denied."
                    except IOError:
                        return "IO Error."
                    except KeyError as err:
                        return f"{file} File name error: {err}"
                    if exif_tags == None or exif_tags == {} or not exif_tags.__contains__('EXIF DateTimeOriginal'):
                        msg = f'[WARN] File does not has EXIF: {file}'
                        do_rename(dirpath, file, db, -1, msg=msg)
                        print(msg)
                    else:
                        exif = str(
                            exif_tags['EXIF DateTimeOriginal']) or None
                        if exif:
                            print(
                                f"[INFO] Match EXIF Time {file} {exif_tags['EXIF DateTimeOriginal']}")
                            do_rename(dirpath, file, db, 0, exif)
                        else:
                            msg = f'[WARN] File does not has Time: {file}'
                            do_rename(dirpath, file, db, -1, msg=msg)
                            print(msg)
            elif match_vid:
                good_vid_pattern = r'VID_\d{8}_\d{6}\.(mp4|MP4|mov|MOV|3gp)'
                next1_vid_pattern = r'VID\d{14}\.(mp4|MP4|mov|MOV)'
                next2_vid_pattern = r'VID_\d{8}_\d{6}_\d+\.(mp4|MP4|mov|MOV)'
                next3_vid_pattern = r'(mmexport|microMsg\.)1[3-6]\d{11}\.(mp4|MP4|mov|MOV)'
                next4_vid_pattern = r'video_\d{8}_\d{6}\.(mp4|MP4|mov|MOV|3gp)'
                if re.match(good_vid_pattern, file):
                    print(f"[ OK ] {file}")
                    count['video'] += 1
                elif re.match(next1_vid_pattern, file):
                    print(f"[INFO] Match timestamp {file}")
                    do_rename(dirpath, file, db, 10)
                    count['dismatch'] += 1
                elif re.match(next2_vid_pattern, file):
                    print(f"[INFO] Match extra text {file}")
                    do_rename(dirpath, file, db, 11)
                    count['dismatch'] += 1
                elif re.match(next3_vid_pattern, file):
                    print(f"[INFO] Match WX timestamp {file}")
                    do_rename(dirpath, file, db, 2)
                    count['dismatch'] += 1
                elif re.match(next4_vid_pattern, file, re.I):
                    print(f"[INFO] Match extra text {file}")
                    do_rename(dirpath, file, db, 12)
                    count['dismatch'] += 1
                else:
                    msg = f'[WARN] Video does not match: {file}'
                    count['dismatch'] += 1
                    do_rename(dirpath, file, db, -1, msg=msg)
                    print(msg)
            else:
                # 不是图片视频
                msg = f'\n[ERROR] File does not match: {file}\n'
                print(msg)
                count['all'] -= 1
                continue
    print("\n[INFO] Result:")
    print(count)
    return "ok"


if __name__ == '__main__':
    ok = main()
    if ok == 'ok':
        print('已检查！\ny -> 进入下一步重命名\ns -> 保存路径并进入下一步重命名\nq -> 退出')
        try:
            todo = input("> ")
        except KeyboardInterrupt:
            quit()

        if todo.lower() == 'y' or todo.lower() == 's':
            if todo.lower() == 's':
                write_preference(DB_NAME, PATH)
            import Rename
            Rename.main(DB_NAME)
            
        else:
            quit()
    else:
        quit(ok)
