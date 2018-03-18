#!/usr/bin/env python3
import sys
import time
import curses
import random
import argparse


def make_argparser():
  parser = argparse.ArgumentParser()
  parser.add_argument('positionals', nargs='*',
    help='Ignored.')
  parser.add_argument('-d', '--dna', action='store_true',
    help='Use random DNA bases instead of random ASCII.')
  parser.add_argument('-l', '--drop-len', type=int,
    help='Use constant-length drops this many characters long.')
  return parser


def main(argv):
  parser = make_argparser()
  args = parser.parse_args(argv[1:])

  with curses_screen() as stdscr:
    (height, width) = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    columns = []
    while True:
      try:
        if args.drop_len:
          drop_len = args.drop_len
        else:
          drop_len = random.randrange(1, 40)
        columns.append({'x':random.randrange(width), 'y':0, 'len':drop_len})
        done = []
        for (i, column) in enumerate(columns):
          if column['y'] >= height + column['len']:
            done.append(i)
            continue
          if args.dna:
            char = random.choice(('A', 'C', 'G', 'T'))
          else:
            char = chr(random.randrange(33, 127))
          try:
            # Draw the character.
            if column['y'] < height:
              draw_char(stdscr, height, width, column['y'], column['x'], char)
            # Delete the character column['len'] before this one.
            if column['y'] - column['len'] >= 0:
              draw_char(stdscr, height, width, column['y'] - column['len'], column['x'], ' ')
            stdscr.refresh()
          except curses.error:
            scr = curses_screen()
            scr.stdscr = stdscr
            scr.__exit__(1, 2, 3)
            sys.stderr.write('curses error on {{add,ins}}chr({}, {}, "{}")\n'
                             .format(column['y'], column['x'], char))
            raise
          column['y'] += 1
          time.sleep(0.002)
        for i in done:
          del(columns[i])
        # time.sleep(0.2)
      except KeyboardInterrupt:
        break


def draw_char(stdscr, height, width, y, x, char):
  if y == height - 1 and x == width - 1:
    # If it's the lower-right corner, addch() throws an error. Use insch() instead.
    stdscr.insch(y, x, char, curses.color_pair(1))
  else:
    stdscr.addch(y, x, char, curses.color_pair(1))


# Create a with context to encapsulate the setup and tear down.
# from http://ironalbatross.net/wiki/index.php?title=Python_Curses
class curses_screen:
    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        self.stdscr.keypad(1)
        return self.stdscr
    def __exit__(self, a, b, c):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()


if __name__ == '__main__':
  sys.exit(main(sys.argv))
