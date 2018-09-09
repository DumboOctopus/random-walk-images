# Random Walk
A random walk is a visual used to see how 'random' and algorithm is.
It involves a Walker which decides whether to go left, right, up, down, etc based
on a random function. As the Walker travels, it marks its path and we see a nice,
random looking pattern show up. The more 'random' it looks, the better the random
algorithm is.
## Why this exists
I thought it looked nice so I wanted to print it on a poster. So I wrote this program to do the hard work of being artistic for me.
If you don't believe me, this was one of the images I produced with `python rwalk.py --width 700 --height 500 -c colors.txt -i 500_00 -b 200 200 200 -f decent-images/thumbnail.jpg`

![Alt text](decent-images/thumbnail.jpg?raw=true "Title")

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
  $ pip -r requirements.txt
```
4. Run it :)
```
  $ python rwalk.py
```
  See `python rwalk.py -h` for a list of all the options.

# Future additions
1. Config files which let you create any number of images which varying configurations.
2. Make a better multi-threaded solution. The problem with the current system is that the overhead from
locking cancels out the benefit of multithreading the randomness. A better system would be to have a painter class
which all the WalkerThreads pass information to paint. This would remove the overhead from locks (as long as I can figure out
  a way of making the recieve method without locks).
3. More expressive syntax for color files. 
3. Gradients. As the walkers move, they gradual shift colors. This could be an array of colors which it lerps between or even just
 a unsynchronized sine waves which vary the color an amount.
