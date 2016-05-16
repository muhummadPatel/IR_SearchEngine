import os


def clean():
    print("rm -rf testbed*_*")
    os.system("rm -rf testbed*_*")


def index_all():
    for i in range(1, 17):
        print("python3 index.py testbed" + str(i))
        os.system("python3 index.py testbed" + str(i))


clean()
index_all()
