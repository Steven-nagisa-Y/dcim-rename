# DCIM Rename tool
## DCIM 是啥

> the DCF specification mandates that a digital camera must store its photos in a "DCIM" directory. DCIM stands for "Digital Camera Images."
> 
> The DCIM directory can — and usually does — contain multiple subdirectories. The subdirectories each consist of a unique three-digit number — from 100 to 999 — and five alphanumeric characters. The alphanumeric characters aren’t important, and each camera maker is free to choose their own. For example, Apple is lucky enough to have a five-digit name, so their code is APPLE. On an iPhone, the DCIM directory contains folders like “100APPLE,” “101APPLE,” and so on.
> 
> Inside each subdirectory are the image files themselves, which represent the photos you take. Each image file’s name starts with a four-digit alphanumberic code — which can be anything the camera maker wants — followed by a four digit number. For example, you’ll often see files named DSC_0001.jpg, DSC_0002.jpg, and so on. The code doesn’t really matter, but it’s consistent to ensure the photos you take are displayed in the order you took them.


## 为啥需要改文件名

众所周知，Android 文件系统就是一个垃圾场，获得 `WRITE_EXTERNAL_STORAGE` 或者 `MANAGE_EXTERNAL_STORAGE` (Adnroid 11) 权限的app可以无限制的读写内部存储空间，就算app使用了推荐的 API 保存照片和视频，文件名也不尽相同。

例如

- QQ | 在QQ中保存的照片、视频（除了通过“我的文件助手”传输的文件外）QQ都会命名为非常奇怪的名字，似乎是`MD5`值的开头。**而且完全没有**EXIF数据，难以对照片、视频进行管理
- 微信 | 微信保存的照片视频还算有良心，一般以mmexport开头，后面接一串13位毫秒级的时间戳，比较容易能转换为时间。


## 目标文件名

- 照片 | IMG_YYYYmmdd_HHMMSS.jpg
- 视频 | VID_YYYYmmdd_HHMMSS.mp4


## 进度

还要继续适配更多的文件名格式...