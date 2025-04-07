# coding=utf-8

import os
from sys import exit
from time import sleep
from tinydb import TinyDB, Query
from pattern_manager import PatternManager


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

def display_todo(db, q):
    paths = [i['path'] for i in db.search(q == 'NEXT')]
    paths = list(set(paths))
    i = 0
    for path in paths:
        print(f"\n-+ {path}")
        for item in db.search(q == 'NEXT'):
            if item['path'] == path:
                print(f" |-+ {item['new']}  <-  {item['original']}")
                i += 1
    print(f"\n[INFO] Total {i} items")


def rename(db, q, i=0):
    """
    执行重命名操作
    
    Args:
        db: TinyDB 数据库实例
        q: Query 对象，用于数据库查询
        i: 重命名方向，0 表示正向重命名，1 表示恢复原名
    """
    rename_list = db.search(q == 'NEXT')
    paths = [i['path'] for i in rename_list]
    paths = list(set(paths))
    
    for path in paths:
        print(f"\n-+ {path}")
        for item in rename_list:
            if item['path'] == path:
                try:
                    old_path = os.path.join(path, item['original'] if i == 0 else item['new'])
                    new_path = os.path.join(path, item['new'] if i == 0 else item['original'])
                    
                    if i == 0:
                        print(f" |-+ Rename to {item['new']}  <-  {item['original']}")
                    else:
                        print(f" |-+ Rename to {item['original']}  <-  {item['new']}")
                    
                    os.rename(old_path, new_path)
                    if os.path.exists(new_path):
                        print("     [ OK ] 改名成功")
                    else:
                        print("     [ERROR] 改名失败")
                    
                except KeyboardInterrupt:
                    quit("User type to quit")
                except PermissionError as err:
                    print(f"     [ERROR] {old_path} Access denied: {err}")
                    continue
                except IOError as err:
                    print(f"     [ERROR] {old_path} IO error: {err}")
                    continue


def main(db_name=None):
    """
    主函数，处理命令行参数并执行相应的重命名操作
    
    Args:
        db_name: 可选的数据库名称
    """
    global DB_NAME
    DB_NAME = db_name
    
    if not DB_NAME:
        print('输入数据库文件名')
        try:
            DB_NAME = input('(Default) photo_db > ')
        except KeyboardInterrupt:
            quit("User type exit")
        except EOFError:
            quit("User type exit")
    
    db = get_db(DB_NAME)
    Photo = Query()
    
    print('\n选择操作：')
    print('all => 显示所有文件')
    print('err => 显示错误文件')
    print('good => 显示正确文件')
    print('next => 显示需要重命名的文件')
    print('rename => 执行重命名')
    print('restore => 恢复原名')
    print('q => 退出')
    
    try:
        select = input('> ')
    except KeyboardInterrupt:
        quit("User type exit")
    except EOFError:
        quit("User type exit")
        
    if select == 'all':
        display_all(db)
    elif select == 'err':
        display_error(db, Photo.status)
    elif select == 'good':
        display_good(db, Photo.status)
    elif select == 'next':
        display_todo(db, Photo.status)
    elif select == 'rename':
        rename(db, Photo.status, 0)
    elif select == 'restore':
        rename(db, Photo.status, 1)
    elif select == 'q':
        quit()
    else:
        print('输入错误！')
        return
    
    return main(DB_NAME)


if __name__ == '__main__':
    import sys
    db_name = ''
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
    main(db_name)
