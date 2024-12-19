import os
import shutil
from stuff.general import General
from tools.helper import get_download_dir, host, print_color, bcolors

class LiteGappsChrome(General):
    dl_links = {
        "11.0.0": {
            "arm64": [
                "https://s3.us-west-2.amazonaws.com/6minutes.io/litegapps/addon/arm64/30/gapps/Chrome/Chrome-LiteGapps-Addon-arm64-11.0.zip",
                "7a0d8c29dfa02d53c0e1421c36f70e1c",
            ],
        },
    }
    arch = host()
    download_loc = get_download_dir()
    dl_file_name = os.path.join(download_loc, "chrome.zip")
    dl_link = ...
    act_md5 = ...
    copy_dir = "./chrome"
    extract_to = "/tmp/chrome/extract"

    def __init__(self, version):
        self.version = version
        self.dl_link = self.dl_links[self.version][self.arch[0]][0]
        self.act_md5 = self.dl_links[self.version][self.arch[0]][1]

    def download(self):
        print_color("Downloading LiteGapps Addon - Chrome now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)

        shutil.copytree(
            os.path.join(self.extract_to, "system", ),
            os.path.join(self.copy_dir, "system"), dirs_exist_ok=True, )
