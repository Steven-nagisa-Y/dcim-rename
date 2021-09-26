# coding=utf-8

import os
from sys import exit
from tinydb import TinyDB, Query


def quit(errMsg=None):
    from time import sleep
    for i in range(1, 4):
        sleep(0.3 * i)
        print(' ' * i + '-> ' + str(i))
    if not errMsg == None:
        print(
            f'[EXIT] Because of  {errMsg}  Program aborted. \nTry again later.')
        exit(1)
    else:
        print(f'[INFO] Good-bye')
        exit(0)


def get_db(db_name='./photo_db.json'):
    if not os.path.exists(db_name):
        quit(f"Do not found DB File {db_name}\n Run Check first.")
    else:
        db = TinyDB(db_name)
        return db


def display_good(db):
    paths = [i['path'] for i in db]
    paths = list(set(paths))
    for path in paths:
        print(f"-+ {path}")
        for item in db:
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")


def display_error(db, q):
    paths = [i['path'] for i in db.search(q == 'ERROR')]
    paths = list(set(paths))
    for path in paths:
        print(f"-+ {path}")
        for item in db.search(q == 'ERROR'):
            if item['path'] == path:
                print(f" |-+ {item['new']}")


def display_good(db, q):
    paths = [i['path'] for i in db.search(q == 'GOOD')]
    paths = list(set(paths))
    for path in paths:
        print(f"-+ {path}")
        for item in db.search(q == 'GOOD'):
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")


def rename(db, q, i=0):
    rename_list = db.search(q == 'GOOD')
    paths = [i['path'] for i in rename_list]
    paths = list(set(paths))
    for path in paths:
        print(f"-+ {path}")
        for item in rename_list:
            if item['path'] == path:
                print(f" |-+ Rename to {item['new']}  <-  {item['original']}")
                try:
                    if i == 0:
                        os.rename(
                            path + os.path.sep + item['original'], path + os.path.sep + item['new'])
                    else:
                        os.rename(
                            path + os.path.sep + item['new'], path + os.path.sep + item['original'])
                except KeyboardInterrupt:
                    quit("User type to quit")
                except PermissionError as err:
                    quit(f"{path + item['original']} access denied: {err}")
                except IOError:
                    quit(f"IO Error.")
                print("     [Ok] 改名成功")


def main():
    db = get_db()
    DCIM = Query()
    print("===========================================================")
    print("功能选择：")
    print("1 => 查看所有数据")
    print("2 => 查看失败的数据")
    print("3 => 查看成功的数据")
    print("4 => 立即重命名")
    print("9 => 重命名恢复")
    print("0 => 退出")
    try:
        select = int(input("> "))
    except KeyboardInterrupt:
        quit()
    except ValueError as err:
        quit(f"Input value error: {err}")
    if select == 0:
        quit()
    if select == 1:
        display_good(db, DCIM.status)
        main()
    if select == 2:
        display_error(db, DCIM.status)
        main()
    if select == 3:
        display_good(db, DCIM.status)
        main()
    if select == 4:
        rename(db, DCIM.status)
        main()
    if select == 9:
        rename(db, DCIM.status, 1)
        main()


if __name__ == '__main__':
    main()
