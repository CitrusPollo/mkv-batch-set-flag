import os
from mkvtool import *
from tkinter.filedialog import askdirectory
from multiprocessing import Process
import time


def main(file):
    mkv_info = read_mkv_info(file)
    mkv_tracks = get_mkv_tracks(mkv_info)
    update_mkv_tracks(file, mkv_tracks)


def start_processes(files):
    for file in files:
        if file.endswith(".mkv"):
            # main(file)
            p = Process(target=main, args=[file])
            p.start()
            processes.append(p)


if __name__ == "__main__":
    os.system("cls")
    path = askdirectory(title="Select Folder")

    start = time.perf_counter()
    processes = list()

    for dirpath, dirname, files in os.walk(path):
        os.chdir(dirpath)
        start_processes(files)

    for process in processes:
        process.join()

    end = time.perf_counter()
    duration = round(end - start, 2)

    exit_message = (
        f"Conversion complete \n" 
        f"Time elapased: {duration} seconds"
        if path
        else "Process cancelled"
    )

    print(exit_message)
