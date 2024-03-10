# coding=utf-8

import os
from sys import exit
from time import sleep
from tinydb import TinyDB, Query


DB_NAME = ''


def quit(errMsg=None):
    if not errMsg == None:
        print(
            f'[EXIT] Because of  {errMsg}  Program aborted. \nTry again later.')
        exit(1)
    else:
        print(f'[INFO] Good-bye')
        exit(0)


def get_db(db_name):
    if not db_name:
        db_name = 'photo_db'
    db_name = f"./{db_name}.json"
    if not os.path.exists(db_name):
        quit(f"Do not found DB File {db_name} Run Check.py first.")
    else:
        db = TinyDB(db_name)
        return db


def display_all(db):
    paths = [i['path'] for i in db]
    paths = list(set(paths))
    for path in paths:
        print(f"\n-+ {path}")
        for item in db:
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")


def display_error(db, q):
    paths = [i['path'] for i in db.search(q == 'ERROR')]
    paths = list(set(paths))
    for path in paths:
        print(f"\n-+ {path}")
        for item in db.search(q == 'ERROR'):
            if item['path'] == path:
                print(f" |-+ {item['new']}")


def display_good(db, q):
    paths = [i['path'] for i in db.search(q == 'GOOD')]
    paths = list(set(paths))
    for path in paths:
        print(f"\n-+ {path}")
        for item in db.search(q == 'GOOD'):
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")


def rename(db, q, i=0):
    rename_list = db.search(q == 'GOOD')
    paths = [i['path'] for i in rename_list]
    paths = list(set(paths))
    for path in paths:
        print(f"\n-+ {path}")
        for item in rename_list:
            if item['path'] == path:
                try:
                    if i == 0:
                        print(f" |-+ Rename to {item['new']}  <-  {item['original']}")
                        os.rename(
                            path + os.path.sep + item['original'], path + os.path.sep + item['new'])
                    else:
                        print(f" |-+ Rename to {item['original']}  <-  {item['new']}")
                        os.rename(
                            path + os.path.sep + item['new'], path + os.path.sep + item['original'])
                except KeyboardInterrupt:
                    quit("User type to quit")
                except PermissionError as err:
                    print(f"     [ERROR] {path + item['original']} Access denied: {err}")
                    sleep(1)
                    continue
                except IOError as err:
                    print(f"     [ERROR] {path + item['original']} IO error: {err}")
                    sleep(1)
                    continue
                print("     [ OK ] 改名成功")


def main(db_name=None):
    global DB_NAME
    print("===========================================================")
    if db_name:
        DB_NAME = db_name
    if not DB_NAME:
        print("输入数据库文件名")
        try:
            DB_NAME = input('(Default) photo_db > ')
        except KeyboardInterrupt:
            quit("Input Database name error")
    db = get_db(DB_NAME)
    DCIM = Query()
    print("功能选择：")
    print("1 => 查看所有数据")
    print("2 => 查看失败的数据")
    print("3 => 查看成功的数据")
    print("8 => 立即重命名")
    print("9 => 重命名恢复")
    print("0 => 退出")
    try:
        select = int(input("> "))
    except KeyboardInterrupt:
        quit()
    except ValueError as err:
        quit(f"请输入数字，而不是 {err}")
    if select == 0:
        quit()
    if select == 1:
        display_all(db)
        main()
    if select == 2:
        display_error(db, DCIM.status)
        main()
    if select == 3:
        display_good(db, DCIM.status)
        main()
    if select == 8:
        rename(db, DCIM.status)
        main()
    if select == 9:
        rename(db, DCIM.status, 1)
        main()
    else:
        print('未知的操作，请重新输入')
        main()


if __name__ == '__main__':
    main()
