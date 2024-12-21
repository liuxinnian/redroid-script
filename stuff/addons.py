import os
import shutil
from stuff.general import General
from tools.helper import get_download_dir, host, print_color, bcolors

class Addons(General):
    dl_links = {
        "11.0.0": {
            "arm64": [
                "https://redroid.s3.us-west-2.amazonaws.com/addons/arm64/30/addons-2024-12-21.zip",
                "a31eff1720f3bced2dc63bc49475c4f5",
            ],
        },
    }
    arch = host()
    download_loc = get_download_dir()
    dl_file_name = os.path.join(download_loc, "addons.zip")
    dl_link = ...
    act_md5 = ...
    copy_dir = "./addons"
    extract_to = "/tmp/addons/extract"

    def __init__(self, version):
        self.version = version
        self.dl_link = self.dl_links[self.version][self.arch[0]][0]
        self.act_md5 = self.dl_links[self.version][self.arch[0]][1]

    def download(self):
        print_color("Downloading Addons now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)

        shutil.copytree(
            os.path.join(self.extract_to),
            os.path.join(self.copy_dir), dirs_exist_ok=True, )
