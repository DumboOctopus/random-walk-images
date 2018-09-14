from PIL import Image, ImageDraw, ImageColor
import random
from threading import Lock, Thread
import re
import argparse
import time
import tqdm
import yaml


class Walker:
    size = 1

    def __init__(self, name, width, height, img_draw, color, iterations, position):
        self.name = name
        self.width = width
        self.height = height
        self.x = position[0]
        self.y = position[1]
        self.img_draw = img_draw
        self.color = color
        self.iterations = iterations

    def full_walk(self):
        for i in tqdm.trange(self.iterations, desc="Walker " + self.name):
            self.draw_step()

    def draw_step(self):
        self.walk()
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
        WalkerThread.counter += 1

    def run(self):
        self.walker.full_walk()


class ParserError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class WalkerConfig:
    def __init__(self, name, color, position, iterations):
        self.name = name
        self.color = color
        self.position = position
        self.iterations = iterations

    def valid(self):
        if self.iterations <= 0:
            return False
        return True


three_tuple_regex = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,?\)\s*?")
hex_regex = re.compile(r"#?([A-Fa-f0-9]{6})")


def parse_color(thing):
    # 3 options, hex, tuple, or dictionary
    if type(thing) == dict:
        try:
            return (
                int(thing['r']),
                int(thing['g']),
                int(thing['b'])
            )
        except ValueError:
            raise ParserError(str(thing), "Each of the values must be an int.")
        except KeyError as e:
            raise ParserError(str(thing), "The " + str(e) + " parameter is missing.")
    elif isinstance(thing, str):
        m = three_tuple_regex.match(thing)
        if m:
            try:
                return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception:
                raise ParserError(thing, "Error while parsing tuple for background color")
        elif hex_regex.match(thing):
            m = hex_regex.match(thing)
            return "#"+m.group(1)
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
    elif isinstance(thing, str):
        if thing.upper() == 'RANDOM':
            return (random.randint(width - int(width * 0.9), int(width * 0.9)),
                    random.randint(height - int(height * 0.9), int(height * 0.9)))
        elif thing.upper() == 'CENTER':
            return (int(width/2.0), int(height/2.0))
    else:
        raise ParserError(thing, "Unknown format for position")


def determine_configs(parser):
    # walker vars -- NOT DEFAULTS!
    walker_configs = []

    TIMESTAMP = str(int(round(time.time() * 1000)))

    # get command line args
    args = parser.parse_args()

    # first read command line args
    # HIGHest priorrity
    thread = args.thread
    width = args.width
    height = args.height
    file = args.file
    background = args.background
    if background is not None: background = tuple(background) # arg parser will give it as an array
    noshow = args.noshow
    iterations = args.iterations

    # Second Read config file if it exists
    if args.config_file:
        try:
            y = yaml.load(args.config_file)

            # if they didn't explicitly say to thread, take the value from config.yaml
            if not args.thread: thread = int(y['thread'])
            width = width or int(y['width'])
            height = height or int(y['height'])
            file = file or y['file']
            file = file.replace("$t", TIMESTAMP)
            try:
                background = background or parse_color(y['background'])
            except ParserError as e:
                e.message += " Location: background."
                raise e
            # if they didn't explicity say noshow, take the value from config.
            if not args.noshow: noshow = y['noshow']
            iterations = iterations or int(y['iterations'])

            # parse walkers:
            for walker in y['walkers']:
                name = None
                for key in walker.keys():
                    if name: raise ParserError(str(walker), "Cannot have multiple walkers in one")
                    name = key
                try:
                    w = WalkerConfig(
                        name,
                        parse_color(walker[name]['color']),
                        parse_position(walker[name]['position'], width, height),  # if a config file is provided, width exists
                        walker[name].get('iterations', iterations)
                    )
                    if w.valid():
                        walker_configs.append(w)
                    else:
                        raise ParserError("Walker " + w.name, "Walker is invalid") from None
                except KeyError as e:
                    raise ParserError("Walker '"+name+"' is missing the "+str(e) + " key", "Walker is invalid") from None
                except Exception:
                    raise ParserError(str(walker.keys()), "Walker is invalid") from None
        except KeyError as e:
            raise ParserError("Source: [Whole file]", "Missing attribute " + str(e) + ".")
        except yaml.YAMLError as exc:
            raise ParserError(str(exc), "Config file is invalid") from None
    # if there wasn't a configuration file then thread, width, etc are equal to stuff from args.

    # -----------3rd Pass assign Defaults------------------------

    width = width or 1000
    height = height or 700
    thread = thread or False
    iterations = iterations or 100_000
    background = background or (45, 45, 45)
    file = file or "out/$t RWalk Image.png".replace("$t", TIMESTAMP)
    walker_configs = walker_configs or [WalkerConfig("walker0", (255, 255, 255), (width / 2, height / 2), iterations)]
    return thread, file, width, height, noshow, background, walker_configs


def run(thread, file, width, height, noshow, background, walker_configs):
    blank_image = Image.new("RGB", (width, height), background)
    img_draw = ImageDraw.Draw(blank_image)
    walkers = list()

    for walker_config in walker_configs:
        walkers.append(Walker(
            walker_config.name,
            width,
            height,
            img_draw,
            walker_config.color,
            walker_config.iterations,
            walker_config.position
        ))

    if thread:
        threads = [WalkerThread(walker) for walker in walkers]
        print(f'Using {len(threads)} threads')
        for thread in threads: thread.start()
        print("Started threads successfully...")
        for thread in threads: thread.join()

        time.sleep(1)
        # for thread in threads: print("")  # print a new line for each progressbar so it doesn't turn out weird
        print("\nDone. Created "+file)
    else:
        print("Working on one thread")
        [walker.full_walk() for walker in walkers]
        print("Done. Created " + file)

    blank_image.save(file)
    blank_image.close()
    if not noshow:
        import webbrowser
        webbrowser.open(file)


if __name__ == "__main__":
    # handle arguments
    parser = argparse.ArgumentParser(description='Create some random walk images')
    # python rwalk.py [configFile] [--options]
    parser.add_argument("config_file", nargs='?', help="path Config File for the walkers", type=argparse.FileType('r'))
    parser.add_argument("--thread",
                        help="Use a seperate thread for each random walker color. May be faster on some computers. Additionally, it makes the colors mesh together instead of overlap",
                        action="store_true")
    parser.add_argument("-f", "--file", help="File path for the picture. Please provide .jpg extention",
                        type=argparse.FileType('w'))
    parser.add_argument("-i", "--iterations", help="Number of iterations of all walkers", type=int)
    parser.add_argument("--width", help="Width of Image", type=int)
    parser.add_argument("--height", help="Width of Image", type=int)
    parser.add_argument("-b", "--background", help="Background color", metavar='B', nargs=3, type=int)
    parser.add_argument("--noshow", action="store_true",
                        help="Do not open the image after generating it. This is useful when you create large images which might cause your image viewer to crash.")

    # Now process all the data and get acutal determine configs
    try:
        thread, file, width, height, noshow, background, walker_configs = determine_configs(parser)

        run(thread, file, width, height, noshow, background, walker_configs)
    except ParserError as e:
        print("An error occured while parsing the configuaration file")
        print("\t" + e.expression)
        print(e.message)
