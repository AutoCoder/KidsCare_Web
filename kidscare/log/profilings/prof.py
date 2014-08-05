# proftest.py
import hotshot.stats
import sys

if __name__ == '__main__':
    if sys.argv:
        stats = hotshot.stats.load(sys.argv[1])
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)