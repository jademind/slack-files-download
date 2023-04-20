#!/usr/bin/python

import argparse
import json
import os
import sys
from typing import List, Optional
from urllib.request import urlopen

"""Downloads all files of messages of your Slack (workspace) JSON export. Each channel
will be processed and a separate folder (default=files) gets created containing all files. 

Usage:
    ./slack-files-download.py YOUR_PATH_TO_SLACK_EXPORT
    ./slack-files-download.py --output NAME_OF_FILES_FOLDER YOUR_PATH_TO_SLACK_EXPORT

Author:
    Andreas Katzian, JadeMind https://jademind.com, 27.06.2022
"""


def is_valid_directory(path: str) -> bool:
    if not os.path.isdir(path):
        return False

    files = ['users.json', 'channels.json']
    missing_files = [f for f in files if not os.path.exists(os.path.join(path, f))]

    return False if missing_files else True


def channel_directories(path: str) -> List[str]:
    files = os.listdir(path)
    return [f for f in files if os.path.isdir(os.path.join(path, f))]


def process_directories(root: str, dirs: List[str], output: str) -> None:
    total_dirs = len(dirs)
    progress(0, total_dirs, suffix='processing channels')

    for index, dir_name in enumerate(dirs, start=1):
        dir_path = os.path.join(root, dir_name)
        output_dir_path = os.path.join(dir_path, output)
        os.makedirs(output_dir_path, exist_ok=True)

        files = os.listdir(dir_path)
        files = [f for f in files if f.lower().endswith('.json')]

        for file in files:
            file_path = os.path.join(dir_path, file)
            data = json.load(open(file_path))
            [process_message(message, output_dir_path, num=index, total=total_dirs) for message in data]

        progress(index, total_dirs, suffix='processed channels')


def process_message(message: json, output_dir_path: str, num: int, total: int) -> None:
    if 'files' in message:
        for item in message['files']:
            if 'id' in item and 'name' in item and 'url_private' in item:
                output_file_name = '_'.join([item['id'], item['name']])
                output_file_path = os.path.join(output_dir_path, output_file_name)

                if os.path.exists(output_file_path):
                    continue

                progress(num, total, suffix=output_file_name)

                try:
                    with urlopen(item['url_private']) as remote_file:
                        with open(output_file_path, 'wb') as download:
                            download.write(remote_file.read())
                except Exception as e:
                    print(e)


# Thanks to Vladimir Ignatyev, https://stackoverflow.com/a/27871113/135160
def progress(count: int, total: int, suffix: Optional[str] = '') -> None:
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write("\033[K")
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process slack exports to download and backup files.')
    parser.add_argument('directory', metavar='dir', type=str, help='the directory of the slack export')
    parser.add_argument('--output', dest='out', type=str, default='files',
                        help='name of downloads folder within channel (default=files)')

    args = parser.parse_args()

    if not is_valid_directory(args.directory):
        sys.exit("The input directory does not seem to contain a slack export.")

    directories = channel_directories(args.directory)
    if not directories:
        sys.exit("The input directory does not contain any channel directories.")

    process_directories(args.directory, directories, output=args.out)
