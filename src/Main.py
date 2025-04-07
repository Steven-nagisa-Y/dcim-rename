# coding=utf-8

import os
import re
from sys import exit
from typing import List, Optional, Tuple, Dict
from tinydb import TinyDB, Query
import exifread
from pattern_manager import PatternManager


DB_NAME = ''
PATH = ''
SAVED_DB = '0_SAVED_PREFERENCE'


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
            print(
                f'已删除{all_pref[select]["db_name"]}：{all_pref[select]["path"]}')
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


def do_rename(dirname, file, db, pattern_info=None, file_path=None, msg=None):
    """
    Rename a file based on pattern info and update the database
    
    Args:
        dirname (str): Directory path
        file (str): Original filename
        db (TinyDB): Database instance
        pattern_info (dict, optional): Pattern matching information
        file_path (str, optional): Full file path for EXIF reading
        msg (str, optional): Error message if rename fails
        
    Returns:
        str: Status of rename operation ('ok' or 'err')
    """
    if msg:
        # Error case - cannot rename
        msg = msg.replace('\n', '')
        db_set(db, dirname, file, msg, status='ERROR')
        return "ok"
        
    if not pattern_info:
        # If no pattern info, try to use EXIF data or creation time
        pattern_manager = PatternManager()
        if pattern_manager.is_image(file):
            pattern_info = {'rename_type': 'exif'}
        else:
            pattern_info = {'rename_type': 'creation_time'}
            
    pattern_manager = PatternManager()
    new_name, error = pattern_manager.generate_new_name(file, pattern_info, file_path)
    
    if error:
        # Log error and mark status as ERROR
        db_set(db, dirname, file, error, status='ERROR')
        return "ok"
        
    if new_name == file:
        # File already has correct name
        db_set(db, dirname, file, file, status='GOOD')
        return "ok"
        
    # File needs to be renamed
    db_set(db, dirname, file, new_name, status='NEXT')
    return "ok"


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
    
    if db_name is None:
        try:
            print("输入数据库文件名")
            db_name = input('(Default) photo_db > ')
        except KeyboardInterrupt:
            return "Input Database name error"
        except ValueError:
            return "Input Database value error"
    db = create_db(db_name)
    global PATH
    PATH = path
    count = {
        'all': 0,
        'good': 0,
        'weird': 0,
        'video': 0
    }
    
    pattern_manager = PatternManager()
    print('[INFO] Start processing...')
    for dirpath, _, files in os.walk(path):
        for file in files:
            count['all'] += 1
            print(f"\rALL: {count['all']} WEIRD: {count['weird']}\n", end='', flush=True)  # 实时更新计数
            file_path = os.path.join(dirpath, file)
            
            if pattern_manager.is_image(file):
                if pattern_manager.is_good_image_name(file):
                    # 将符合规范的文件也记录到数据库中
                    db_set(db, dirpath, file, file)
                    count['good'] += 1
                else:
                    pattern_info = pattern_manager.get_image_pattern_match(file)
                    if pattern_info:
                        print(f"[INFO] Match {pattern_info['description']} {file}")
                        do_rename(dirpath, file, db, pattern_info, file_path)
                        count['weird'] += 1
                    else:
                        count['weird'] += 1
                        # Try EXIF-based rename
                        dt_str = pattern_manager.get_file_datetime(file_path)
                        if dt_str:
                            pattern_info = {'rename_type': 'exif'}
                            do_rename(dirpath, file, db, pattern_info, file_path)
                        else:
                            msg = f'[WARN] File does not has EXIF: {file}'
                            do_rename(dirpath, file, db, None, None, msg=msg)
                            print(msg)
                            
            elif pattern_manager.is_video(file):
                count['video'] += 1
                if pattern_manager.is_good_video_name(file):
                    # 将符合规范的文件也记录到数据库中
                    db_set(db, dirpath, file, file)
                    count['good'] += 1
                else:
                    pattern_info = pattern_manager.get_video_pattern_match(file)
                    if pattern_info:
                        print(f"[INFO] Match {pattern_info['description']} {file}")
                        do_rename(dirpath, file, db, pattern_info)
                        count['weird'] += 1
                    else:
                        # Try creation time based rename
                        pattern_info = {'rename_type': 'creation_time'}
                        do_rename(dirpath, file, db, pattern_info, file_path)
                        count['weird'] += 1
            else:
                # 不是图片或视频文件
                msg = f'\n[ERROR] File does not match: {file}\n'
                print(msg)
                count['all'] -= 1
                continue

    print(f"\n[INFO] 处理完成")
    print(f"[INFO] 共发现{count['all']}个文件")
    print(f"[INFO] 其中视频{count['video']}个")
    print(f"[INFO] 规范文件名{count['good']}个")
    print(f"[INFO] 需要修改{count['weird']}个")
    write_preference(DB_NAME, path)
    return "ok"


if __name__ == '__main__':
    ok = main()
    if ok == 'ok':
        print('已检查！\ny -> 进入下一步重命名\n\nq -> 退出')
        try:
            todo = input("> ")
        except KeyboardInterrupt:
            quit()

        if todo.lower() == 'y':
            import Rename
            Rename.main(DB_NAME)

        else:
            quit()
    else:
        quit(ok)
