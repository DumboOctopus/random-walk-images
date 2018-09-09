# Random Walk
A random walk is a visual used to see how 'random' and algorithm is.
It involves a Walker which decides whether to go left, right, up, down, etc based
on a random function. As the Walker travels, it marks its path and we see a nice,
random looking pattern show up. The more 'random' it looks, the better the random
algorithm is.
![Alt text](decent-images/thumbnail.jpg?raw=true "Title")
Produced with `python rwalk.py --width 700 --height 500 -c colors.txt -i 500_00 -b 200 200 200 -f decent-images/thumbnail.jpg`
## Why this exists
I thought it looked nice so I wanted to print it on a poster. So I wrote this program to do the hard work of being artistic for me.

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
