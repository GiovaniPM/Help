#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

import curses
import os

MENU = "menu"
COMMAND = "command"
EXITMENU = "exitmenu"
SEPARATOR = "separator"

def read_str(stdscr, y, x, label, size):
    curses.echo()
    stdscr.addstr(y, x, label)
    inputtext = ' '
    stdscr.addstr(y, x + len(label), inputtext.rjust(size, ' '))
    fieldtext = stdscr.getstr(y, x + len(label), size)
    curses.noecho()
    return fieldtext

def draw_box(stdscr, yini, xini, yfin, xfin):
    text1 = '-'
    text2 = ' '
    stdscr.addstr(yini, xini, '+' + text1.rjust(xfin - xini - 1, '-') + '+')
    if (xfin - xini) > 1:
        for y in range(yfin - yini - 1):
            stdscr.addstr(yini + y + 1, xini, '|' +
                          text2.rjust(xfin - xini - 1, ' ') + '|')
        stdscr.addstr(yfin, xini, '+' +
                      text1.rjust(xfin - xini - 1, '-') + '+')

def border_box(stdscr, yini, xini, yfin, xfin):
    text1 = '-'
    text2 = ' '
    stdscr.addstr(yini, xini, '+' + text1.rjust(xfin - xini - 1, '-') + '+')
    if (xfin - xini) > 1:
        for y in range(yfin - yini - 1):
            stdscr.addstr(yini + y + 1, xini, '|')
            stdscr.addstr(yini + y + 1, xfin, '|')
        stdscr.addstr(yfin, xini, '+' +
                      text1.rjust(xfin - xini - 1, '-') + '+')

def runMenu(screen, menu, parent, getin=0):

    h = curses.color_pair(1)
    n = curses.A_NORMAL

    if parent is None:
        lastoption = "Sair"
    else:
        print(parent['title'])
        lastoption = "Voltar ao menu %s" % parent['title']

    optioncount = len(menu['options'])  # how many options in this menu

    pos = getin
    oldpos = None
    x = None

    while x != ord('\n'):
        if pos != oldpos:
            oldpos = pos
            screen.border(0)
            screen.addstr(0, 2, " " + menu['title'] + " ", curses.A_STANDOUT)
            screen.addstr(2, 2, menu['subtitle'], curses.color_pair(4))

            for index in range(optioncount):
                textstyle = n
                if pos == index:
                    textstyle = h
                if menu['options'][index]['type'] == MENU:
                    screen.addstr(4+index, 4, "%2d - >%s<" %
                                  (index+1, menu['options'][index]['title']), textstyle)
                else:
                    screen.addstr(4+index, 4, "%2d - %s" %
                                  (index+1, menu['options'][index]['title']), textstyle)
            textstyle = curses.color_pair(3)
            if pos == optioncount:
                textstyle = curses.color_pair(2)
            screen.addstr(6+optioncount, 4, "%d - %s" %
                          (optioncount+1, lastoption), textstyle)
            screen.refresh()

        curses.noecho()
        x = screen.getch()  # Gets user input

        if x == curses.KEY_HOME:
            pos = 0
        elif x == curses.KEY_END:
            pos = optioncount
        elif x == curses.KEY_DOWN:  # 258: # down arrow
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == curses.KEY_RIGHT:  # down right
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == curses.KEY_UP:  # 259: # up arrow
            if pos > 0:
                pos += -1
            else:
                pos = optioncount
        elif x == curses.KEY_LEFT:  # up left
            if pos > 0:
                pos += -1
            else:
                pos = optioncount

    return pos

def processArg(screen, menu, getin):
    screen.clear()
    comnando = ''
    try:
        comando = menu['options'][getin]['command']
        if menu['options'][getin]['params'] != None:
            # draw_box(screen, 1, 1, 25, 118)
            screen.border(0)
            pos = 5
            for arg in menu['options'][getin]['params']:
                param = read_str(
                    screen, pos, 2, arg.rjust(12, ' ') + ": ", 100)
                # border_box(screen, 1, 1, 25, 118)
                screen.border(0)
                pos = pos + 1
                comando = comando + " " + param.decode('ascii')
    except:
        comando = menu['options'][getin]['command']
    os.system('reset')
    os.system("cls")
    os.system("echo %s" % comando)
    os.system(comando)
    os.system("pause")

def processMenu(screen, menu, parent=None):
    optioncount = len(menu['options'])
    exitmenu = False
    getin = 0
    while not exitmenu:
        getin = runMenu(screen, menu, parent, getin)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] == COMMAND:
            curses.def_prog_mode()
            if menu['options'][getin]['title'] == 'Pianobar':
                os.system('amixer cset numid=3 1')
            screen.clear()
            processArg(screen, menu, getin)
            screen.clear()
            curses.reset_prog_mode()
            curses.curs_set(1)
            curses.curs_set(0)
            os.system('amixer cset numid=3 2')
        elif menu['options'][getin]['type'] == MENU:
            screen.clear()
            processMenu(screen, menu['options'][getin], menu)
            screen.clear()
        elif menu['options'][getin]['type'] == EXITMENU:
            exitmenu = True

def createMenu(menu_data):
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    screen.keypad(1)
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    processMenu(screen, menu_data)

    curses.endwin()