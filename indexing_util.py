import os


def clean():
    print("rm -rf testbed*_*")
    os.system("rm -rf testbed*_*")


def index_all():
    for i in range(1, 17):
        if i != 10:
            print("python3 index.py testbed" + str(i))
            os.system("python3 index.py testbed" + str(i))


def clean_and_index(i):
    os.system("rm -rf " + str(i) + "_*")
    os.system("python3 index.py " + str(i))


if __name__ == "__main__":
    clean()
    index_all()
