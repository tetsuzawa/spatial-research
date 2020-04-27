#!/usr/bin/env python3
# coding: utf-8

import sys

import pandas as pd


def main():
    args = sys.argv

    df = pd.read_csv(args[1], header=None)

    accuracy = sum(df[6]) / len(df[6]) * 100
    print(f"accuracy: {accuracy:.1f}%")


if __name__ == '__main__':
    main()
