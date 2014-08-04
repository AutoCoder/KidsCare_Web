# proftest.py
import hotshot.stats

stats = hotshot.stats.load("seriesofbrand-20140804T011044.prof")
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(20)