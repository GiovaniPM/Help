import time,sys

#╔══════════╦════════════════════════════════╦═════════════════════════════════════════════════════════════════════════╗
#║  Code    ║             Effect             ║                                   Note                                  ║
#╠══════════╬════════════════════════════════╬═════════════════════════════════════════════════════════════════════════╣
#║ 0        ║  Reset / Normal                ║  all attributes off                                                     ║
#║ 1        ║  Bold or increased intensity   ║                                                                         ║
#║ 2        ║  Faint (decreased intensity)   ║  Not widely supported.                                                  ║
#║ 3        ║  Italic                        ║  Not widely supported. Sometimes treated as inverse.                    ║
#║ 4        ║  Underline                     ║                                                                         ║
#║ 5        ║  Slow Blink                    ║  less than 150 per minute                                               ║
#║ 6        ║  Rapid Blink                   ║  MS-DOS ANSI.SYS; 150+ per minute; not widely supported                 ║
#║ 7        ║  [[reverse video]]             ║  swap foreground and background colors                                  ║
#║ 8        ║  Conceal                       ║  Not widely supported.                                                  ║
#║ 9        ║  Crossed-out                   ║  Characters legible, but marked for deletion.  Not widely supported.    ║
#║ 10       ║  Primary(default) font         ║                                                                         ║
#║ 11–19    ║  Alternate font                ║  Select alternate font `n-10`                                           ║
#║ 20       ║  Fraktur                       ║  hardly ever supported                                                  ║
#║ 21       ║  Bold off or Double Underline  ║  Bold off not widely supported; double underline hardly ever supported. ║
#║ 22       ║  Normal color or intensity     ║  Neither bold nor faint                                                 ║
#║ 23       ║  Not italic, not Fraktur       ║                                                                         ║
#║ 24       ║  Underline off                 ║  Not singly or doubly underlined                                        ║
#║ 25       ║  Blink off                     ║                                                                         ║
#║ 27       ║  Inverse off                   ║                                                                         ║
#║ 28       ║  Reveal                        ║  conceal off                                                            ║
#║ 29       ║  Not crossed out               ║                                                                         ║
#║ 30–37    ║  Set foreground color          ║  See color table below                                                  ║
#║ 38       ║  Set foreground color          ║  Next arguments are `5;n` or `2;r;g;b`, see below                       ║
#║ 39       ║  Default foreground color      ║  implementation defined (according to standard)                         ║
#║ 40–47    ║  Set background color          ║  See color table below                                                  ║
#║ 48       ║  Set background color          ║  Next arguments are `5;n` or `2;r;g;b`, see below                       ║
#║ 49       ║  Default background color      ║  implementation defined (according to standard)                         ║
#║ 51       ║  Framed                        ║                                                                         ║
#║ 52       ║  Encircled                     ║                                                                         ║
#║ 53       ║  Overlined                     ║                                                                         ║
#║ 54       ║  Not framed or encircled       ║                                                                         ║
#║ 55       ║  Not overlined                 ║                                                                         ║
#║ 60       ║  ideogram underline            ║  hardly ever supported                                                  ║
#║ 61       ║  ideogram double underline     ║  hardly ever supported                                                  ║
#║ 62       ║  ideogram overline             ║  hardly ever supported                                                  ║
#║ 63       ║  ideogram double overline      ║  hardly ever supported                                                  ║
#║ 64       ║  ideogram stress marking       ║  hardly ever supported                                                  ║
#║ 65       ║  ideogram attributes off       ║  reset the effects of all of 60-64                                      ║
#║ 90–97    ║  Set bright foreground color   ║  aixterm (not in standard)                                              ║
#║ 100–107  ║  Set bright background color   ║  aixterm (not in standard)                                              ║
#╚══════════╩════════════════════════════════╩═════════════════════════════════════════════════════════════════════════╝

def loading():
    print("Loading...")
    for i in range(0, 100):
        time.sleep(0.1)
        sys.stdout.write(u"\u001b[1000D" + str(i + 1) + "%")
        sys.stdout.flush()
    print()

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

# A List of Items
items = list(range(0, 200))
l = len(items)

# Initial call to print 0% progress
printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 100)
for i, item in enumerate(items):
    # Do stuff...
    time.sleep(0.1)
    # Update Progress Bar
    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 100)

#loading()

for i in range(0, 16):
    for j in range(0, 16):
        code = str(i * 16 + j)
        saida = "[38;5;" + code + "m"
        sys.stdout.write(u"\u001b[38;5;" + code + "m " + saida.ljust(10))
    print(u"\u001b[0m")

for i in range(0, 16):
    for j in range(0, 16):
        code = str(i * 16 + j)
        saida = "[48;5;" + code + "m"
        sys.stdout.write(u"\u001b[48;5;" + code + "m " + saida.ljust(10))
    print(u"\u001b[0m")