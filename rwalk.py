from PIL import Image, ImageDraw, ImageColor
import random
from threading import Lock, Thread
import sys
from ast import literal_eval
import re
import argparse
import time
import tqdm


class Walker:
    size = 1
    def __init__(self, width, height, img_draw, color, iterations=1000, random_position=False):
        self.width = width
        self.height = height
        if random_position:
            self.x = random.randint(0, int(self.width*0.8))
            self.y = random.randint(0, int(self.height*0.8))
        else:
            self.x = width/2 # we will use this as center
            self.y = height/2
        self.img_draw = img_draw
        self.color = color
        self.iterations = iterations

    def full_walk(self):
        for i in tqdm.trange(self.iterations, desc="Color "+str(self.color)):
            self.draw_step()

    def draw_step(self):
        self.walk()
#        self.img_draw.rectangle((self.x, self.y, self.x + Walker.size, self.y + Walker.size),fill=self.color,outline=self.color)
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

line_pattern = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*(random)?")
def parse_color_file_line(line):
    m = line_pattern.match(line)
    if m:
        tmp = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        rand = m.group(4) == 'random'
        return tmp, rand
    return None, False


if __name__ == "__main__":


    # handle arguments
    parser = argparse.ArgumentParser(description='Create some random walk images')
    parser.add_argument("--thread", help="Use a seperate thread for each random walker color. May be faster on some computers. Additionally, it makes the colors mesh together instead of overlap", action="store_true")
    parser.add_argument("-c", "--colors", help="File path to a colors document. See colors.txt for syntax. Default is to have one black walker originating from the center")
    parser.add_argument("-f", "--file", help="File path for the picture. Please provide .jpg extention")
    parser.add_argument("-i", "--iterations", help="Number of iterations of all walkers", type=int, default=10000)
    parser.add_argument("--width", help="Width of Image", type=int, default=12*50)
    parser.add_argument("--height", help="Width of Image", type=int, default=18*50)
    parser.add_argument("-b", "--background", help="Background color", metavar='B', nargs=3, type=int, default = [255,255,255])
    parser.add_argument("--noshow", action="store_true", help="Do not open the image after generating it. This is useful when you create large images which might cause your image viewer to crash.")

    args = parser.parse_args()


    blank_image = Image.new("RGB", (args.width, args.height), tuple(args.background))
    img_draw = ImageDraw.Draw(blank_image)
    walkers = list()

    if args.colors:
        file = open(args.colors)
        i = 0
        for line in file:
            if '#' in line: continue
            if len(line) < 2: continue

            color, random_position = parse_color_file_line(line)
            if color:
                print("Using color " + str(color) + (" with random positioning" if random_position else ""))
                walkers.append(Walker(args.width, args.height, img_draw, color, iterations=args.iterations, random_position=random_position))

            i+=1

        file.close()
    if args.iterations:
        for walker in walkers:
            walker.iterations = args.iterations
    if args.file:
        filename = args.file
    else:
        filename = 'out/RWALK'+str(int(round(time.time() * 1000)))+f'with {args.background} {args.iterations} {args.colors} {"threaded" if args.thread else ""}.jpg'

    # assign default values if they weren't assigned by arguments
    if len(walkers) < 1:
        walkers.append(Walker(args.width, args.height, img_draw, (0,0,0), iterations=args.iterations))


    if args.thread:

        threads = [WalkerThread(walker) for walker in walkers]
        print(f'Using {len(threads)} threads')
        for thread in threads: thread.start()
        print("Started threads successfully...")
        for thread in threads: thread.join()
        for thread in threads: print("") # print a new line for each progressbar so it doesn't turn out weird
        print("\nDone")
    else:
        print("Working on one thread")
        #[walker.full_walk(lock=False) for walker in walkers]
        [walker.full_walk() for walker in walkers]
        print("Done")
        #w1.full_walk(lock=False)




    blank_image.save(filename)
    blank_image.close()
    if not args.noshow:
        import webbrowser
        webbrowser.open(filename)
