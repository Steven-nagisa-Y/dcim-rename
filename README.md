# DCIM Rename tool
## DCIM 是啥

> the DCF specification mandates that a digital camera must store its photos in a "DCIM" directory. DCIM stands for "Digital Camera Images."
>
> The DCIM directory can — and usually does — contain multiple subdirectories. The subdirectories each consist of a unique three-digit number — from 100 to 999 — and five alphanumeric characters. The alphanumeric characters aren’t important, and each camera maker is free to choose their own. For example, Apple is lucky enough to have a five-digit name, so their code is APPLE. On an iPhone, the DCIM directory contains folders like “100APPLE,” “101APPLE,” and so on.
>
> Inside each subdirectory are the image files themselves, which represent the photos you take. Each image file’s name starts with a four-digit alphanumberic code — which can be anything the camera maker wants — followed by a four digit number. For example, you’ll often see files named DSC_0001.jpg, DSC_0002.jpg, and so on. The code doesn’t really matter, but it’s consistent to ensure the photos you take are displayed in the order you took them.

## 为啥需要改文件名

众所周知，Android 文件系统就是一个垃圾场，app可以无限制的读写内部存储空间，就算app使用了推荐的 API 保存照片和视频，文件名也不尽相同。

例如

- QQ | 在QQ中保存的照片、视频（除了通过“我的文件助手”传输的文件外）QQ都会命名为非常奇怪的名字，似乎是`MD5`值的开头。**而且完全没有**EXIF数据，难以对照片、视频进行管理
- 微信 | 微信保存的照片视频还算有良心，一般以mmexport开头，后面接一串13位毫秒级的时间戳，比较容易能转换为时间。

## 本脚本目的

- 尽可能通过文件名推断出拍摄日期，如没有则读取EXIF信息获取拍摄日期
- 批量重命名照片、视频文件，使其符合我个人强迫症文件名的要求。

### 当前支持的 patterns

```python
good_img_pattern = r'((IMG|PANO|Screenshot|PXL)_\d{8}_\d{6}(_HDR)?(_\w+\.\w+\..+)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG))'

next1_img_pattern = r'\d{13}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
next2_img_pattern = r'IMG_\d{8}_\d{6}.+\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
next3_img_pattern = r'IMG\d{14}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
next4_img_pattern = r'(mmexport|microMsg\.|Image_)\d{13}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
next5_img_pattern = r'\d{8}_\d{6}(_HDR)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
next6_img_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}\.\d{2}\.\d{2}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)'
```

### 目标文件名

- 照片 | `IMG_YYYYmmdd_HHMMSS.jpg`
- 视频 | `VID_YYYYmmdd_HHMMSS.mp4`

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python Check.py
```

<a href="https://github.com/Steven-nagisa-Y/dcim-rename">
  <img align="center" src="https://github-readme-stats.vercel.app/api/pin/?username=Steven-nagisa-Y&repo=dcim-rename" />
</a>
