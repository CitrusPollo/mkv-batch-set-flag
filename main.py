import os
from mkvtool import *
from tkinter.filedialog import askdirectory
from multiprocessing import Process
import time


def read_mkv(file):

    mkv_info = read_mkv_info(file)
    mkv_tracks = get_mkv_tracks(mkv_info)
    update_mkv_tracks(file, mkv_tracks)


def start_processes(files):
    for file in files:
        if file.endswith(".mkv"):
            # main(file)
            p = Process(target=read_mkv, args=[file])
            p.start()
            processes.append(p)


def measure_duration(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        duration = round(end - start, 2)
        exit_message = (
            f"Conversion complete \nTime elapased: {duration} seconds"
            if path
            else "Process cancelled"
        )
        print(exit_message)

    return wrapper


@measure_duration
def main(path):
    global processes
    processes = list()
    for dirpath, dirname, files in os.walk(path):
        os.chdir(dirpath)
        start_processes(files)

    for process in processes:
        process.join()


if __name__ == "__main__":
    os.system("cls")
    window_title = "Select directory with mkv files"
    path = askdirectory(title=window_title)
    main(path)
