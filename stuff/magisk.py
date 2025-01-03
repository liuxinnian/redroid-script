import gzip
import os
import shutil
import re
from stuff.general import General
from tools.helper import bcolors, download_file, host, print_color, run, get_download_dir

class Magisk(General):
    download_loc = get_download_dir()
    dl_link = "https://redroid.s3.us-west-2.amazonaws.com/magisk/Magisk-v27.0.apk"
    dl_file_name = os.path.join(download_loc, "magisk.apk")
    act_md5 = "4475064c5f6a5474e31f2f3dfafc22ed"
    extract_to = "/tmp/magisk_unpack"
    copy_dir = "./magisk"
    magisk_dir = os.path.join(copy_dir, "system", "etc", "init", "magisk")
    machine = host()
    oringinal_bootanim = """
service bootanim /system/bin/bootanimation
    class core animation
    user graphics
    group graphics audio
    disabled
    oneshot
    ioprio rt 0
    task_profiles MaxPerformance
    
"""
    bootanim_component = """
on post-fs-data
    start logd
    
    # Debug logging
    exec u:r:su:s0 root root -- log -p i -t Magisk "Starting Magisk initialization"
    
    # Check SELinux status
    exec u:r:su:s0 root root -- log -p i -t Magisk "SELinux status:"
    exec u:r:su:s0 root root -- getenforce
    
    # Check initial file permissions
    exec u:r:su:s0 root root -- log -p i -t Magisk "Initial magisk directory contents:"
    exec u:r:su:s0 root root -- ls -laZ /system/etc/init/magisk/
    
    # Setup Magisk working directory
    mkdir /data/adb 755
    mkdir /data/adb/magisk 755
    mkdir /data/adb/magisk/modules 755
    mkdir /data/adb/magisk/mirror 755
    mkdir /data/adb/magisk/post-fs-data.d 755
    mkdir /data/adb/magisk/service.d 755
    
    exec u:r:su:s0 root root -- log -p i -t Magisk "Created magisk directories"
    
    # Start magisk daemon
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magisk{arch} --daemon
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magiskpolicy --live --magisk "allow * magisk_file lnk_file *"
    
    # Setup runtime mount points
    mkdir /sbin/.magisk 700
    mkdir /sbin/.magisk/mirror 700
    mkdir /sbin/.magisk/block 700
    mkdir /sbin/.magisk/worker 700
    
    copy /system/etc/init/magisk/config /sbin/.magisk/config
    rm /dev/.magisk_unblock
    exec u:r:su:s0 root root -- /sbin/magisk --post-fs-data
    wait /dev/.magisk_unblock 40
    rm /dev/.magisk_unblock

on zygote-start
    exec u:r:su:s0 root root -- /sbin/magisk --zygote-restart

on property:sys.boot_completed=1
    # Check final file structure and permissions
    exec u:r:su:s0 root root -- log -p i -t Magisk "Final file permissions check:"
    exec u:r:su:s0 root root -- ls -laZ /system/etc/init/magisk/
    exec u:r:su:s0 root root -- ls -laZ /data/adb/magisk/
    exec u:r:su:s0 root root -- ls -laZ /sbin/.magisk/
    
    # Check SELinux contexts
    exec u:r:su:s0 root root -- log -p i -t Magisk "Final SELinux status:"
    exec u:r:su:s0 root root -- getenforce
    exec u:r:su:s0 root root -- ls -Z /system/etc/init/magisk/
    
    # Ensure proper permissions
    exec u:r:su:s0 root root -- /system/bin/chcon u:object_r:magisk_file:s0 /data/adb/magisk
    exec u:r:su:s0 root root -- /system/bin/chown -R root:root /data/adb/magisk
    exec u:r:su:s0 root root -- /system/bin/chmod -R 755 /data/adb/magisk
    exec u:r:su:s0 root root -- /sbin/magisk --boot-complete
    exec -- /system/bin/sh -c "if [ ! -e /data/data/com.topjohnwu.magisk ] ; then pm install /system/etc/init/magisk/magisk.apk ; fi"
   
on property:init.svc.zygote=restarting
    exec u:r:su:s0 root root -- /sbin/magisk --zygote-restart
   
on property:init.svc.zygote=stopped
    exec u:r:su:s0 root root -- /sbin/magisk --zygote-restart
    """.format(arch=machine[1])

    def download(self):
        print_color("Downloading Magisk v27 official release now .....", bcolors.GREEN)
        super().download()   

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.magisk_dir):
            os.makedirs(self.magisk_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.copy_dir, "sbin")):
            os.makedirs(os.path.join(self.copy_dir, "sbin"), exist_ok=True)

        print_color("Copying magisk libs now ...", bcolors.GREEN)
        
        arch_map = {
            "x86": "x86",
            "x86_64": "x86_64",
            "arm": "armeabi-v7a",
            "arm64": "arm64-v8a"
        }
        lib_dir = os.path.join(self.extract_to, "lib", arch_map[self.machine[0]])
        for parent, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                o_path = os.path.join(lib_dir, filename)  
                filename = re.search('lib(.*)\.so', filename)
                n_path = os.path.join(self.magisk_dir, filename.group(1))
                shutil.copyfile(o_path, n_path)
                run(["chmod", "+x", n_path])
        shutil.copyfile(self.dl_file_name, os.path.join(self.magisk_dir,"magisk.apk") )

        # Updating Magisk from Magisk manager will modify bootanim.rc, 
        # So it is necessary to backup the original bootanim.rc.
        bootanim_path = os.path.join(self.copy_dir, "system", "etc", "init", "bootanim.rc")
        gz_filename = os.path.join(bootanim_path)+".gz"
        with gzip.open(gz_filename,'wb') as f_gz:
            f_gz.write(self.oringinal_bootanim.encode('utf-8'))
        with open(bootanim_path, "w") as initfile:
            initfile.write(self.oringinal_bootanim+self.bootanim_component)

        os.chmod(bootanim_path, 0o644)
