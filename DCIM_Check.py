# coding=utf-8

import os
import re
from sre_constants import NOT_LITERAL
from sys import exit
from tinydb import TinyDB, Query
import exifread


def select_path():
    print("===========================================================")
    print("请输入需要处理的目录，例如：/DCIM/Camera ")
    print("输入 img 处理当前目录下 img ")
    try:
        src = input("> ")
    except KeyboardInterrupt:
        quit("User type exit")
    if src == 'img':
        _path = os.getcwd() + os.path.sep + 'img'
    elif src == 't':
        _path = '/Volumes/NAS/_My/Phone/DCIM/'
    else:
        _path = src
    if not os.path.exists(_path):
        print("路径无效！")
        return "err"
    return _path


def create_db(db_name='./photo_db.json'):
    if os.path.exists(db_name):
        os.remove(db_name)
    db = TinyDB(db_name)
    return db


def db_set(db, path, ori, new, status='GOOD'):
    ori = str(ori)
    new = str(new)
    db.insert({'path': path, 'original': ori, 'new': new, 'status': status})
    return db.all()


def db_get(db, query, value):
    return db.search(query == value)


def do_rename(dirname, file, db, i, t=None, msg=None):
    match_name = re.match(r'^(?P<name>[\S\s]+)\.(?P<ext>\S+)$', file)
    file_name = match_name.groupdict()['name']
    file_ext = match_name.groupdict()['ext']
    file_ext = file_ext.lower()
    if i == 0:
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

    if i == -1:
        if msg:
            # 无法自动重命名
            msg = msg.replace('\n', '')
            db_set(db, dirname, file, msg, status='ERROR')
            return "ok"
        else:
            return "err"


def quit(errMsg=None):
    from time import sleep
    for i in range(1,4):
        sleep(0.3 * i)
        print(' ' * i + '-> ' + str(i))
    if not errMsg == None:
        print(
            f'[EXIT] Because of  {errMsg}  Program aborted. \nTry again later.')
        exit(1)
    else:
        print(f'[INFO] Good-bye')
        exit(0)


def main():
    path = select_path()
    if path != "err":
        db = create_db()
        count = {
            'all': 0,
            'good': 0,
            'dismatch': 0,
            'video': 0
        }
        img_pattern = r'.+\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
        vid_pattern = r'.+\.(mp4|MP4|mov|MOV)'
        for dirpath, _, files in os.walk(path):
            for file in files:
                count['all'] += 1
                match_img = re.match(img_pattern, file)
                match_vid = re.match(vid_pattern, file)
                if match_img:
                    good_img_pattern = r'((IMG|PANO)_\d{8}_\d{6}(_HDR)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG))|(IMG_\d+\.(heic|HEIC))'
                    next1_img_pattern = r'16\d{11}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                    next2_img_pattern = r'IMG_\d{8}_\d{6}.+\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                    next3_img_pattern = r'IMG\d{14}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
                    if re.match(good_img_pattern, file):
                        print(f"[GOOD] {file}")
                        count['good'] += 1
                    elif re.match(next1_img_pattern, file):
                        do_rename(dirpath, file, db, 1)
                        count['dismatch'] += 1
                    elif re.match(next2_img_pattern, file):
                        do_rename(dirpath, file, db, 11)
                        count['dismatch'] += 1
                    elif re.match(next3_img_pattern, file):
                        do_rename(dirpath, file, db, 10)
                        count['dismatch'] += 1
                    else:
                        count['dismatch'] += 1
                        f = open(dirpath + os.path.sep + file, 'rb')
                        exif_tags = exifread.process_file(f)
                        f.close()
                        if exif_tags == None or exif_tags == {} or not exif_tags.__contains__('EXIF DateTimeOriginal'):
                            msg = f'\n[ERROR] File does not has EXIF: {file}\n'
                            do_rename(dirpath, file, db, -1, msg=msg)
                            print(msg)
                        else:
                            exif = str(
                                exif_tags['EXIF DateTimeOriginal']) or None
                            if exif:
                                print(
                                    f"[INFO] File {file} Time {exif_tags['EXIF DateTimeOriginal']}")
                                do_rename(dirpath, file, db, 0, exif)
                            else:
                                msg = f'\n[ERROR] File does not has Time: {file}\n'
                                do_rename(dirpath, file, db, -1, msg=msg)
                                print(msg)
                elif match_vid:
                    good_vid_pattern = r'VID_\d{8}_\d{6}\.(mp4|MP4|mov|MOV)'
                    next1_vid_pattern = r'VID\d{14}\.(mp4|MP4|mov|MOV)'
                    next2_vid_pattern = r'VID_\d{8}_\d{6}_\d+\.(mp4|MP4|mov|MOV)'
                    if re.match(good_vid_pattern, file):
                        count['video'] += 1
                    elif re.match(next1_vid_pattern, file):
                        do_rename(dirpath, file, db, 10)
                        count['dismatch'] += 1
                    elif re.match(next2_vid_pattern, file):
                        do_rename(dirpath, file, db, 11)
                        count['dismatch'] += 1
                    else:
                        msg = f'\n[ERROR] Video does not match: {file}\n'
                        count['dismatch'] += 1
                        do_rename(dirpath, file, db, -1, msg=msg)
                        print(msg)
                else:
                    msg = f'\n[ERROR] File does not match: {file}\n'
                    count['dismatch'] += 1
                    print(msg)
                    return f"Unkown File {file}"
        print("\n[INFO] Result:")
        print(count)
        return "ok"
    else:
        return "Selected path is not exist"


if __name__ == '__main__':
    ok = main()
    if ok == 'ok':
        quit()
    else:
        quit(ok)
