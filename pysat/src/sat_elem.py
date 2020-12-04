def main():
    with open("ELEM.TXT", mode="r") as elem_file:
        sat_name = elem_file.readline()
        # 行を捨てる
        line = elem_file.readline().split(" ")[1:]
        line




if __name__ == '__main__':
    main()
