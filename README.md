# Random Walk
![python rwalk.py example-config-files/example.yaml --width 1000 --height 100 -i 20000 -b 40 40 40](decent-images/banner.jpg?raw=true "Banner")
A random walk is a visual used to see how 'random' and algorithm is.
It involves a Walker which decides whether to go left, right, up, down, etc based
on a random function. As the Walker travels, it marks its path and we see a nice,
random looking pattern show up. The more 'random' it looks, the better the random
algorithm is.
## Why this exists
I thought it looked nice so I wanted to print it on a poster. So I wrote this program to do the hard work of being artistic for me.
This was one of the images I produced with `python rwalk.py example-config-files/example.yaml --width 1000 --height 700 -i 100_000 -b 45 45 45 -f decent-images/thumbnail.jpg`

![Alt text](decent-images/thumbnail.jpg?raw=true "Oooo pretty colors")

## Set Up
1. Initialize a virtual environment:
```
  $ virtualenv -p python3 venv
```
2. Activate it:
```
  $ source venv/bin/activate
```
3. Install the requirements
```
  $ pip install -r requirements.txt
```
4. Run it :)
```
  $ python rwalk.py
```
  See `python rwalk.py -h` for a list of all the options.

## Documentation
### Parameters
Rwalk has several global configurations. These configurations apply to the whole image:
1. `background`: background color
2. `width`: width of image (in pixels)
3. `height`: height of image (in pixels)
4. `file`: file name of the generated image
5. `iterations`: default iterations for all walkers
6. `noshow`: whether or not to open the image after creating it
7. `thread`: whether or not to make each walker run on a seperate thread

Walkers walk around the image randomly and wherever they go, they leave their color behind. 
Rwalk can run any number of walkers. Here are configurations for walkers:
1. `iterations`: how many steps should the walker travel
2. `color`: what color trail they leave behind
3. `position`: where they start in the image

If iterations is provided inside the walker, it will override the global iterations provided. 

## Overriding 

If you want to override anything in a configuration file without actually changing it
you can simply provide command line args. For example if width was 1000 in the configuration
file but you want it 2000:
```
 python rwalk.py path/to/config.yaml --width 2000
```

These are the available command line args:
1. `--thread`
2. `-f FILE `
3. `-i ITERATIONS`
4. `--width WIDTH`
5. `--height HEIGHT`
6. `-b R G B`
7. `--noshow`

Note: iterations will override the GLOBAL iterations variable in the configuration but it will 
NOT override for any walkers which individually override iterations

## Syntax of Configuration files
The configuration file are written in yaml like so:
```yaml
background:
  r: 45
  b: 45
  g: 45
width: 1000
height: 700
iterations: 100_000 # default iterations for all walkers.
thread: no
noshow: no
file: out/example$t.jpg # the $t is replaced with a timestamp. Useful for getting unique filenames
walkers:
  # a list of all the walkers
  - blue: # Name of walker the names don't matter. It will be used when displaying progress bars
      color: "#7e93cc"
      position: random
      iterations: 400_000 # setting the iterations for THIS walker to 400_000
  - yellow:
      color: (251, 197, 49)
      position: (250, 250) # coordinates start from upper left hand corner
  - red:
      color: (241, 90, 89)
      position: random
  - purple:
      color: (120, 83, 162)
      position: random
```

For colors, one can write them in 3 ways.
1. Tuple: (redValue, greenValue, blueValue)
2. hex: "45f3Ed" or "#45f3Ed"
  WARNING: be sure to wrap the hex in quotes. 
3. dictionary:
  ```yaml
   background:
     r: 255
     g: 255
     b: 255
  ```

For positions, there are 3 options:
1. Tuple: (xValue, yValue)
2. random: simply write the word random
  ```yaml
    position: random
  ```
3. center: simply write the word center. Starts walkers in the center

## Tips

### Finding Good Colors
Color Hunt (colorhunt.co) is a great place to find palletes of matching colors. I would recommend colors which do not contrast
too much. The random walks often overlap so having too much contrast would make it look off. However, having
a background which contrasts the walks can be totally valid and looks great. (For example, having electric blue
walkers on a stormy grey/black background). 

## How many Walkers?
I would recommend 1, 3 or 4 walkers. Two walkers is harder to pull off because you have less colors. However, one can work because there isn't any other walkers it's colors will interact with. Four is difficult but it can be pulled off. If you try 4, I would recommend setting the iterations for each walker individually (using the iterations: <int> attribute). If all walkers walk for the same amount, there can be too much going on. If they walk for too little, it would look incomplete. So therefore, try to make certain colors walk more than others. 

## Workflow?
When using rwalk.py, you can override the configuration file's rules with the command line args 
(like `python rwalk.py config.yaml -i 100_000`). This is easier than modifying the the configuration
file each time you want to experiment with different iterations, backgrounds, etc
