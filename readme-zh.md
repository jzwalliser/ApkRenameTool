English | [中文](readme_zh.md)

# 简介
这款软件可以帮你重命名安卓的安装包文件。它支持的文件格式包括apk、apkm、apks、xapk。

|格式|支持平台|
|:-|:-|
|`.apk`|全平台（Windows/macOS/Linux）|
|`.apkm`/`.apks`/`.xapk`|Linux 发行版（或其他支持  `archivemount`的操作系统|

工具通过解析安装包内部的元数据（应用名称、版本号、最低 Android 版本、支持的 CPU 架构等），按自定义模板自动生成清晰、统一的文件名。

# 安装
在Linux发行版上，需要安装`archivemount`、`aapt`（这里以Ubuntu为例）：
```bash
$ sudo apt install archivemount aapt
```
然后把源代码直接下载下来，用Python编译器执行就可以了。

注意，Windows操作系统需要额外下载`aapt.exe`，并把它和此工具放在同一目录下。

# 内部工作原理&设计
## 原理（`apk`）
1. 运行aapt命令来解析apk，获取原始输出。
2. 通过正则匹配，提取出apk文件的名称、包名、版本、支持的CPU架构等信息。
3. 最后，根据模板对文件进行重命名。
## 原理（`apkm`、`apks`、`xapk`）
1. 调用`archivemount`，把文件挂载到本地。
2. 扫描挂载目录内所有的 split APK 文件，逐一用  `aapt`解析。
3. 将所有信息汇总起来。
4. 最后，根据模板对文件进行重命名。

## 设计考量
1. `archivemount`：特殊的安装包文件（`apkm`、`apks`、`xapk`）的本质其实是zip压缩包，里面包含若干个split apk文件；由于`aapt`无法直接进压缩包读取apk，所以用`archivemount`给它挂载到本地，这样还省去了解压的步骤
2. `aapt`：这个命令很好用，可快速的解析出apk的信息

# 使用参数
- `-d` / `--dir`：指定需要批量重命名的目录，默认为当前运行目录`./`
- `-f` / `--file`：指定需要重命名的单个文件
- `-t` / `--template`：自定义重命名的文件名模板，默认模板：`{app_name} [{version_name}, Android {android_ver}+] ({', '.join(native_code)}){suffix}`，下面会详细解释
- `-e` / `--filetype`：如果传入的某个文件后缀名很奇怪（例如f.zip），但它实际上就是apk文件，那么可以通过该参数直接给他指定为apk文件，由此绕过后缀名检查；请注意，如果重命名一整个目录下的文件，那么它会把整个目录中的所有文件都当成指定的类型；若不指定则仅处理支持的格式
- `-n` / `--dry-run`：试运行模式，仅输出重命名预览，不会实际修改文件名
- `-v` / `--verbose`：开启详细日志，输出更多日志和错误信息

# 命名模板的使用
通过`-e`/`--template`参数可以自定义模板。例如，file.apk：
|变量名|说明|示例值|
|:-|:-|:-|
|`appname`|应用显示名称|`'哔哩经典'`|
|`package_name`|应用包名|`'tv.biliclassic'`|
|`version_name`|版本名称|`'0.4.10'`|
|`version_code`|版本号（数字）|`'4100'`|
|`min_sdk`|最低SDK版本|`3`|
|`android_ver`|最低支持的 Android 版本|`'1.5'`|
|`nativecode`|支持的 CPU 架构列表|`['arm64-v8a', 'armeabi', 'armeabi-v7a', 'mips', 'x86']`|
|`suffix`|原始文件后缀（含点）|`.apk`|

那么，执行这个：
```bash
$ python3 rename.py -f file.apk -t '{appname} {version_code}{suffix}'
```
会将`file.apk`会重命名成`哔哩经典 0.4.10.apk`

程序中的默认模板是这样的：
```
{app_name} [{version_name}, Android {android_ver}+] ({', '.join(native_code)}){suffix}
```
于是会重命名为：`哔哩经典 [0.4.10, Android 1.5+] (arm64-v8a, armeabi, armeabi-v7a, mips, x86).apk`

# 致谢
在此，感谢各位开发者们写出了超好用的库和CLI工具！ 