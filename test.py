'''
from PIL import Image, ImageDraw
im = Image.fromarray(A, mode="CMYK")
im.save("your_file.jpeg")
'''
from PIL import Image, ImageDraw, ImageColor
import random
from threading import Lock, Thread
import sys
from ast import literal_eval
import re
import argparse

class Walker:
    lock = Lock()
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

    def full_walk(self, lock=True):
        if lock:
            for i in range(self.iterations):
                self.draw_step_with_lock()
        else:
            for i in range(self.iterations):
                self.draw_step_without_lock()

    def draw_step_with_lock(self):#, debug_number=None):
        self.walk()
        with Walker.lock:
            self.img_draw.rectangle((self.x, self.y, self.x + Walker.size, self.y + Walker.size),fill=self.color,outline=self.color)

    def draw_step_without_lock(self):
        self.walk()
        self.img_draw.rectangle((self.x, self.y, self.x + Walker.size, self.y + Walker.size),fill=self.color,outline=self.color)


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
      self.number = WalkerThread.counter
      WalkerThread.counter +=1

    def run(self):
        print(str(self.number) + ":Running")
        self.walker.full_walk()
        print(str(self.number) + "-----------Finished-----------")

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
    parser.add_argument("--thread", help="Use a seperate thread for each random walker color. May be faster on some computers", action="store_true")
    parser.add_argument("-c", "--colors", help="File path to a colors document")
    parser.add_argument("-f", "--file", help="File path for the picture. Please provide .jgp extention", default="drawn_image.jpg")
    parser.add_argument("-i", "--iterations", help="Number of iterations of all walkers", type=int, default=10000)
    parser.add_argument("--width", help="Width of Image", default=12*50)
    parser.add_argument("--height", help="Width of Image", default=18*50)
    parser.add_argument("-b", "--background", help="Background color", metavar='B', nargs=3, type=int, default = [255,255,255])

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
    if args.iterations:
        for walker in walkers:
            walker.iterations = args.iterations
    if args.file:
        filename = args.file

    # assign default values if they weren't assigned by arguments
    if len(walkers) < 1:
        walkers.append(Walker(args.width, args.height, img_draw, (0,0,0), iterations=args.iterations))


    if args.thread:

        threads = [WalkerThread(walker) for walker in walkers]
        print(f'Using {len(threads)} threads')
        for thread in threads: thread.start()
        print("Started threads successfully...")
        for thread in threads: thread.join()
        print("Done")
    else:
        print("Working on one thread")
        [walker.full_walk(lock=False) for walker in walkers]
        print("Done")
        #w1.full_walk(lock=False)




    blank_image.save(filename)
    import webbrowser
    webbrowser.open(filename)
