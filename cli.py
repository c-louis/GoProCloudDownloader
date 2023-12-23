import sys
import getopt
from explorer_v2 import ExplorerV2
import utils

from tqdm import tqdm

def help(name, error=None):
    if error is not None:
        print(f"{error}\n")
    print(f"python3 {name}     ")
    print("\t-u <urls separated by ,>")
    print("\t-z <zip or not (True|False)>")
    print("\t-s <max file size (for zip)>>")
    print("\t-f <max file in zip>")
    print("\t-q <quality (hd or source)>")
    print("\t-d <simultanate>")
    print("\nDefault is: zip with 5gb files and 50 files by zip and 5 download at a time maximum")
    print("You cant zip in source quality")

def main(argv):
    urls = None
    # -h for help
    z = True                    # -z Zip or Not
    zip_max_size = 5e9          # -s 5Gb
    zip_max_file = 50           # -f 50 files by zip
    quality = "hd"              # -q Default quality to HD
    simultanate_download = 2    # -d Simulatanate
    dry_run = None
    download_path = "./"
    debug = None

    opts, args = getopt.getopt(argv[1:], "hz:s:f:q:d:u::", ["zip=", "zip_max_size=", "zip_max_file=", "quality=", "simultanate_download=", "urls=", "dry_run", "download_path=", "debug"])
    for opt, arg in opts:
        if opt == '-h':
            help(argv[0])
            return 0
        elif opt in ("-z", "--zip"):
            if arg not in ("True", "False"):
                help(argv[0], f"'{arg}' is not a valid zip argument. Valid values are: 'True' and 'False'")
                return 1
            z = True if arg == "True" else False
        elif opt in ("-s", "--zip_max_size"):
            zip_max_size = int(arg)
        elif opt in ("-f", "--zip_max_file"):
            zip_max_file = int(arg)
        elif opt in ("-q", "--quality"):
            if arg not in ("hd", "source"):
                help(argv[0], f"'{arg}' is not a valid quality. Valid values are: 'hd' and 'source'")
                return 1
            quality = arg
        elif opt in ("-d", "--simultanate_download"):
            simultanate_download = int(arg)
        elif opt in ("-u", "--urls"):
            urls = arg.split(",")
        elif opt == "--dry_run":
            dry_run = True
        elif opt == "--download_path":
            download_path = arg
        elif opt == "--debug":
            debug = True
    if urls is None or len(urls) == 0:
        help(argv[0], "urls cant be empty")
        return 1
    for url in urls:
        valid, error = utils.check_url(url)
        if not valid:
            help(argv[0], error)
            return 1
    if debug:
        print(opts)

    explorer = ExplorerV2(z, zip_max_size, zip_max_file, quality, simultanate_download, dry_run, download_path, debug)
    explorer.explore_all(urls)

    media_count = len(explorer.get_medias_list()) if explorer.zip is False or explorer.quality == "source" else len(explorer.split_for_zip())
    pbu = utils.ProgressBarUtils(simultanate_download, media_count, explorer.get_medias_total_size())
    callbacks = pbu.get_callbacks()
    explorer.download_all(download_callbacks=callbacks)
    #explorer.download_all(download_callbacks=utils.dc_text)


if __name__ == "__main__":
    main(sys.argv)