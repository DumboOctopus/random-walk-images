from PIL import Image, ImageDraw, ImageColor
import random
from threading import Lock, Thread
import sys
from ast import literal_eval
import re
import argparse
import time
import tqdm
import yaml
from exception import Exception


class Walker:
    size = 1
    def __init__(name, self, width, height, img_draw, color, iterations, position):
        self.name = name
        self.width = width
        self.height = height
        self.x = position[0]
        self.y = position[1]
        self.img_draw = img_draw
        self.color = color
        self.iterations = iterations

    def full_walk(self):
        for i in tqdm.trange(self.iterations, desc="Color "+str(self.color)):
            self.draw_step()

    def draw_step(self):
        self.walk()
        #self.img_draw.rectangle((self.x, self.y, self.x + Walker.size, self.y + Walker.size),fill=self.color,outline=self.color)
        self.img_draw.point((self.x, self.y), fill=self.color)

    def walk(self):

        self.x += self.size * random.randint(-2, 2)
        self.y += self.size * random.randint(-2, 2)
        if self.x < 0:
            self.x = self.width - self.size
        elif self.x > self.width:
            self.x = 0

        if self.y < 0:
            self.y = self.height - self.size
        elif self.y > self.height:
            self.y = 0

class WalkerThread(Thread):
    counter = 0
    def __init__(self, walker):
      Thread.__init__(self)
      self.walker = walker
      self.id = WalkerThread.counter
      WalkerThread.counter +=1

    def run(self):
        self.walker.full_walk()

class ParserError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class WalkerConfig:
    def __init__(name, color, position, iterations):
        self.name = name
        self.color = color
        self.position = position
        self.iterations = iterations

    def valid():
        if self.iterations <= 0:
            return False
try:
    print("hi")
except Exception:
    pass

three_tuple_regex = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,?\)\s*?")
hex_regex = re.compile(r"#[A-Fa-f0-9]{6}")
def parse_color(thing):
    # 3 options, hex, tuple, or dictionary
    if type(thing) == dict:

        try:
            #return (int(thing['r']), int(thing['b']), int(thing['c'])
            return "hi"
        except ValueError:
            raise ParserError(str(thing), "Invalid format for background color")
    elif isinstance(thing, basestring):
        m = three_tuple_regex.match(thing)
        if m:
            try:
                return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception:
                raise ParserError(thing, "Error while parsing tuple for background color")
        elif hex_regex.match(thing):
            return thing
    else:
        raise ParserError(thing, "Unknown format for background color")


two_tuple_regex = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,?\)\s*?")
def parse_position(thing, width, height):
    # return random or a tuple
    m = two_tuple_regex.match(thing)
    if m:
        try:
            return (int(m.group(1)), int(m.group(2)))
        except Exception:
            raise ParserError(thing, "Error while parsing tuple for position")
    elif isinstance(thing, basestring) and thing.upper() == 'RANDOM':
        return (random.randint(width - int(width*0.9), int(width*0.9)), random.randint(height - int(height*0.9), int(height*0.9))
    else:
        raise ParserError(thing, "Unknown format for position")

def determine_configs(parser):
    # walker global vars -- NOT DEFAULTS!
    thread = None
    file = None
    width = None
    height = None
    noshow = None
    background = None
    walker_configs = []

    TIMESTAMP = str(int(round(time.time() * 1000)))

    # get command line args
    args = parser.parse_args()

    # first read command line args
    # HIGHest priorrity
    width = args.width
    height = args.height
    file = args.file
    background = args.background
    noshow = args.noshow


    # Second Read config file if it exists
    if args.config_file:
        try:
            y = yaml.load(args.config_file)
            background = parse_color(y['background'])
            width = int(y['width'])
            height = int(y['height'])
            iterations = int(y['iterations'])
            thread = int(y['thread'])
            noshow = y['noshow']
            file = y['file'].replace("$t", TIMESTAMP)

            # parse walkers:
            for walker in y['walkers']:
                try:
                    w = WalkerConfig(
                        walker.keys()[0],
                        parse_color(walker['color']),
                        parse_position(walker['position'], width, height), # if a config file is provided, width exists
                        walker['iterations']
                    )
                    if w.valid():
                        walker_configs.append(w)
                    else:
                        raise ParserError("Walker " + w.name, "Walker is invalid")

                except Exception:
                    raise ParserError(str(walker.keys()), "Walker is valid")

        except yaml.YAMLError as exc:
            raise ParserError(str(exc), "Config file is invalid")
            print(exc)

    # 3rd pass. assign Defaults
    width = width or 500
    height = height or 700
    thread = thread or False
    file = file or "out/$t RWalk Image.png".replace("$t", TIMESTAMP)
    background = background or (0, 0, 0)
    walker_configs = walker_configs or [WalkerConfig("walker0", (255, 255, 255), (width/2, height/2))]
    # DO NOT OVERRIDE  noshow
    return thread, file, width, height, noshow, background, walkers_configs

def run(thread, file, width, height, noshow, background, walker_configs):
    blank_image = Image.new("RGB", (width, height), background)
    img_draw = ImageDraw.Draw(blank_image)
    walkers = list()

    for walker_config in walker_configs:
        walkers.append(
            walker_config.name,
            width,
            height,
            img_draw,
            walker_config.color,
            walker_config.iterations,
            walker_config.position
        )

    if thread:
        threads = [WalkerThread(walker) for walker in walkers]
        print(f'Using {len(threads)} threads')
        for thread in threads: thread.start()
        print("Started threads successfully...")
        for thread in threads: thread.join()
        for thread in threads: print("") # print a new line for each progressbar so it doesn't turn out weird
        print("\nDone")
    else:
        print("Working on one thread")
        [walker.full_walk() for walker in walkers]
        print("Done")

    blank_image.save(filename)
    blank_image.close()
    if not noshow:
        import webbrowser
        webbrowser.open(filename)

if __name__ == "__main__":

    # handle arguments
    parser = argparse.ArgumentParser(description='Create some random walk images')
    # python rwalk.py [configFile] [--options]
    parser.add_argument("config_file", help="path Config File for the walkers", type=argparse.FileType('r'), default=None)
    parser.add_argument("--thread", help="Use a seperate thread for each random walker color. May be faster on some computers. Additionally, it makes the colors mesh together instead of overlap", action="store_true")
    parser.add_argument("-f", "--file", help="File path for the picture. Please provide .jpg extention", type=argparse.FileType('w'))
    parser.add_argument("-i", "--iterations", help="Number of iterations of all walkers", type=int, default=10000)
    parser.add_argument("--width", help="Width of Image", type=int, default=12*50)
    parser.add_argument("--height", help="Width of Image", type=int, default=18*50)
    parser.add_argument("-b", "--background", help="Background color", metavar='B', nargs=3, type=int, default = [255,255,255])
    parser.add_argument("--noshow", action="store_true", help="Do not open the image after generating it. This is useful when you create large images which might cause your image viewer to crash.")


    # Now process all the data and get acutal determine configs
    thread, file, width, height, noshow, background, walker_configs = determine_configs(parser)

    run(thread, file, width, height, noshow, background, walker_configs)
