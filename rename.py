import subprocess
import re
import os
import traceback
import argparse
import pathlib

parser = argparse.ArgumentParser(description="APK Rename Tool: Renames APK files based on their metadata. Supported formats: apk, xapk, apks, apkm. If a file with an unsupported suffix is provided, it will be ignored unless the -e or --filetype option is used.
")
group = parser.add_mutually_exclusive_group()
group.add_argument("-d","--dir",default="./",help="Rename items in the specified directory.")
group.add_argument("-f","--file",help="Rename a single file.")
parser.add_argument("-t","--template",default="{app_name} [{version_name}, Android {android_ver}+] ({', '.join(native_code)}){suffix}",help="Specify a rename template.")
parser.add_argument("-e","--filetype",default=None,help="Specify a file type explicitly. Defaults to matching by suffix if not provided.")
parser.add_argument("-n","--dry-run",action="store_true",help="Perform a dry run without making changes.")
parser.add_argument("-v","--verbose",action="store_true",help="Show detailed logs and errors.")
args = parser.parse_args()

def parse_apk(apk_path):
    result = subprocess.run(["aapt","dump","badging",apk_path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    output = result.stdout
    package_match = re.search(
        r"package: name='(.*?)' versionCode='(.*?)' versionName='(.*?)'",
        output
    )
    if package_match:
        package_name = package_match.group(1)
        version_code = package_match.group(2)
        version_name = package_match.group(3)
    else:
        raise ValueError

    label_match = re.search(r"application-label:'(.*?)'",output)
    app_name = label_match.group(1) if label_match else "Unknown"
    
    try:
        native_code_match = re.search(r"native-code: (.*)",output)
        native_code = native_code_match.group(1).strip()
    except:
        native_code = "noarch"
        
    min_sdk_match = re.search(r"sdkVersion:'([^']+)'",output)
    min_sdk = int(min_sdk_match.group(1)) if min_sdk_match else "unknown"
    
    return {"app_name":app_name,"package_name":package_name,"version_name":version_name,"version_code":version_code,"native_code":sorted(native_code.replace("'","").split()),"min_sdk":min_sdk}

def parse_split_apks(split_apks_path):
    native_code = []
    if not os.path.exists("./mnt"):
        os.mkdir("./mnt")
    result = subprocess.run(["archivemount","-o","readonly",split_apks_path,"./mnt"],capture_output=True,text=True)
    if result.returncode:
        raise NameError(result.stderr)
    for i in os.listdir("./mnt"):
        try:
            if i.endswith(".apk"):
                info = parse_apk(f"./mnt/{i}")
                if info["app_name"] != "Unknown":
                    app_name = info["app_name"]
                    package_name = info["package_name"]
                    version_name = info["version_name"]
                    version_code = info["version_code"]
                    min_sdk = info["min_sdk"]
                native_code = native_code + info["native_code"]
        except:
            raise ValueError
    subprocess.run(["umount","-l","./mnt"])
    native_code = sorted(list(set(native_code)))
    if len(native_code) >= 2 and "noarch" in native_code:
        native_code.remove("noarch")
    return {"app_name":app_name,"package_name":package_name,"version_name":version_name,"version_code":version_code,"native_code":native_code,"min_sdk":int(min_sdk)}

sdk2android = {3:"1.5",4:"1.6",5:"2.0",6:"2.0.1",7:"2.1",8:"2.2",9:"2.3",10:"2.3.3",11:"3.0",12:"3.1",13:"3.2",14:"4.0",15:"4.0.3",16:"4.1",17:"4.2",18:"4.3",19:"4.4",20:"4.4W",21:"5.0",22:"5.1",23:"6.0",24:"7.0",25:"7.1",26:"8.0",27:"8.1",28:"9",29:"10",30:"11",31:"12",32:"12L",33:"13",34:"14",35:"15"}

def rename(file,filetype=None,dry_run=False,verbose=True):
    try:
        path = pathlib.Path(file)
        if path.is_dir():
            return
        suffix = path.suffix
        if filetype:
            suffix = filetype
            if not suffix.startswith("."):
                suffix = "." + suffix
        directory = path.parent
        if suffix == ".apk":
            info = parse_apk(file)
        elif suffix in [".xapk",".apks",".apkm"]:
            info = parse_split_apks(file)
        
        if suffix in [".apk",".xapk",".apks",".apkm"]:
            app_name = info['app_name']
            package_name = info["package_name"]
            version_name = info["version_name"]
            version_code = info["version_code"]
            min_sdk = info["min_sdk"]
            android_ver = sdk2android[min_sdk]
            native_code = info["native_code"]
            template = f"f\"{args.template}\""
            rename = (file,os.path.join(directory,eval(template)))
            if pathlib.Path(rename[0]).name != pathlib.Path(rename[1]).name:
                if not dry_run:
                    os.rename(*rename)
                print("[+] Rename:",rename[0],"->",rename[1])
            else:
                print("[+] Okay:",rename[0])
    except:
        print("[!] Rename failed:",file)
        if verbose:
            traceback.print_exc()

if args.file:
    rename(args.file,args.filetype,args.dry_run,args.verbose)
else:
    for i in os.listdir(args.dir):
        rename(os.path.join(args.dir,i),args.filetype,args.dry_run,args.verbose)