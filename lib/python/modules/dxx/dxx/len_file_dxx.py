#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

import dxx


def main():
    desc = "len_file_dxx prints length of .DXX file"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filename", help="filename to analyze")
    args = parser.parse_args()
    filename = args.filename

    input_ext = os.path.splitext(filename)[-1]
    if input_ext in dxx.exts:
        data = dxx.read(filename)

    else:
        print("Error: input file extension is invalid. want: .DXX, got:", input_ext, file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    print(f"{len(data)} [sample]")


if __name__ == '__main__':
    main()
