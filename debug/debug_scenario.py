"""Skenario debugging (Praktikum 5): dua bug yang sengaja dibuat, lalu diperbaiki.

  python debug/debug_scenario.py 1   -> bug 1: ZeroDivisionError (ada traceback)
  python debug/debug_scenario.py 2   -> bug 2: bug logika tanpa exception (nilai 0 ditolak)
"""
import sys


def buggy_average(scores):
    return sum(scores) / len(scores)          # BUG 1: list kosong -> bagi nol


def fixed_average(scores):
    if not scores:                            # FIX: guard clause
        return None
    return sum(scores) / len(scores)


def buggy_valid_score(score):
    if not score:                             # BUG 2: 0 dianggap "kosong"
        return False
    return type(score) is int and 0 <= score <= 100


def fixed_valid_score(score):
    return type(score) is int and 0 <= score <= 100   # FIX: tanpa truthiness


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "1"
    if mode == "1":
        print("Rata-rata:", buggy_average([]))
    else:
        for value in (None, 0, 100, 101):
            print(f"{value!r:>5} buggy={buggy_valid_score(value)!s:<6} fixed={fixed_valid_score(value)}")
        print("fixed_average([]) =", fixed_average([]))
