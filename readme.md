English | [中文](readme_zh.md)

# Introduction
This software helps you rename Android installation package files. Supported file formats include `apk`, `apkm`, `apks`, and `xapk`.

|Format|Supported Platforms|
|:-|:-|
|`.apk`|All platforms (Windows/macOS/Linux)|
|`.apkm`/`.apks`/`.xapk`|Linux distributions (or other operating systems that support `archivemount`)|

By parsing the metadata inside the installation package (app name, version number, minimum Android version, supported CPU architectures, etc.), the tool automatically generates clear and consistent file names according to a customizable template.

# Installation
On Linux distributions, you need to install `archivemount` and `aapt` (using Ubuntu as an example):
```bash
$ sudo apt install archivemount aapt
```
Then simply download the source code and run it with the Python interpreter.

Note: On Windows, you need to download `aapt.exe` separately and place it in the same directory as this tool.

# Internal Mechanism & Design
## Mechanism (`apk`)
1. Run the `aapt` command to parse the APK and obtain the raw output.
2. Extract information such as the APK file's name, package name, version, and supported CPU architectures using regex matching.
3. Finally, rename the file according to the template.

## Mechanism (`apkm`, `apks`, `xapk`)
1. Run `archivemount` to mount the file locally.
2. Scan all split APK files within the mounted directory and parse each one using `aapt`.
3. Aggregate all the extracted information.
4. Finally, rename the file according to the template.

## Design Considerations
1. `archivemount`: Special package files (`apkm`, `apks`, `xapk`) are essentially ZIP archives containing multiple split APK files. Since `aapt` cannot directly read APKs from within a compressed archive, `archivemount` is used to mount the file locally, which also eliminates the need for extraction.
2. `aapt`: This command is very handy and can quickly parse APK information.

# Usage Parameters
- `-d`/`--dir`: Specify the directory for batch renaming; defaults to the current working directory `./`
- `-f`/`--file`: Specify a single file to rename
- `-t`/`--template`: Customize the file name template for renaming; default template: `{app_name} [{version_name}, Android {android_ver}+] ({', '.join(native_code)}){suffix}`; detailed explanation below
- `-e`/`--filetype`: If a file has an unusual extension (e.g., `.f.zip`) but is actually an APK file, you can use this parameter to explicitly specify its type, bypassing the file extension check; note: if renaming all files within a directory, all files in that directory will be treated as the specified type; if not specified, only supported formats will be processed
- `-n`/`--dry-run`: Dry-run mode, only outputs a preview of the renaming operation without actually modifying any file names
- `-v` / `--verbose`: Enable verbose logging for more detailed logs and error messages

# Using Naming Templates
You can customize the template using the `-t` / `--template` parameter. For example, for `file.apk`:

|Variable Name|Description|Example Value|
|:-|:-|:-|
|`appname`|App display name|`'哔哩经典'`|
|`package_name`|App package name|`'tv.biliclassic'`|
|`version_name`|Version name|`'0.4.10'`|
|`version_code`|Version code (numeric)|`'4100'`|
|`min_sdk`|Minimum SDK version|`3`|
|`android_ver`|Minimum supported Android version|`'1.5'`|
|`nativecode`|List of supported CPU architectures|`['arm64-v8a', 'armeabi', 'armeabi-v7a', 'mips', 'x86']`|
|`suffix`|Original file extension (including the dot)|`.apk`|

Then, running this:
```bash
$ python3 rename.py -f file.apk -t '{appname} {version_code}{suffix}'
```
will rename `file.apk` to `哔哩经典 0.4.10.apk`.

The default template in the program is:
```
{app_name} [{version_name}, Android {android_ver}+] ({', '.join(native_code)}){suffix}
```
This would rename the file to: `哔哩经典 [0.4.10, Android 1.5+] (arm64-v8a, armeabi, armeabi-v7a, mips, x86).apk`

# Acknowledgements
I would like to express my gratitude to all the developers who have created these incredibly useful libraries and CLI tools!