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
    db_name = f"./Database/{db_name}.json"
    if not os.path.exists(db_name):
        quit(f"Do not found DB File {db_name} Run Check.py first.")
    else:
        db = TinyDB(db_name)
        return db


def display_all(db):
    paths = [i['path'] for i in db]
    paths = list(set(paths))
    i = 0
    for path in paths:
        print(f"\n-+ {path}")
        for item in db:
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")
                i += 1
    print(f"\n[INFO] Total {i} items")


def display_error(db, q):
    paths = [i['path'] for i in db.search(q == 'ERROR')]
    paths = list(set(paths))
    i = 0
    for path in paths:
        print(f"\n-+ {path}")
        for item in db.search(q == 'ERROR'):
            if item['path'] == path:
                print(f" |-+ {item['new']}")
                i += 1
    print(f"\n[INFO] Total {i} items")


def display_good(db, q):
    paths = [i['path'] for i in db.search(q == 'GOOD')]
    paths = list(set(paths))
    i = 0
    for path in paths:
        print(f"\n-+ {path}")
        for item in db.search(q == 'GOOD'):
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")
                i += 1
    print(f"\n[INFO] Total {i} items")


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
                    continue
                except IOError as err:
                    print(f"     [ERROR] {path + item['original']} IO error: {err}")
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
    print("a => 查看所有数据")
    print("f => 查看失败的数据")
    print("s => 查看成功的数据")
    print("r => 立即重命名")
    print("b => 重命名恢复")
    print("c => 检查其他文件夹")
    print("q => 退出")
    try:
        select = input("> ")
    except KeyboardInterrupt:
        quit()
    if select == 'q':
        quit()
    if select == 'a':
        display_all(db)
        main()
    if select == 'f':
        display_error(db, DCIM.status)
        main()
    if select == 's':
        display_good(db, DCIM.status)
        main()
    if select == 'r':
        rename(db, DCIM.status)
        main()
    if select == 'b':
        rename(db, DCIM.status, 1)
        main()
    if select == 'c':
        import Main
        Main.main()
        return
    else:
        print('未知的操作，请重新输入')
        main()


if __name__ == '__main__':
    import sys
    db_name = ''
    if len(sys.argv) == 2:
        db_name = sys.argv[1]
    main(db_name)
