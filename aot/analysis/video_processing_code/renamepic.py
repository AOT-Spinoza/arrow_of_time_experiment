import os
import sys


path = '/Users/shufanzhang/Documents/PhD/Arrow_of_time/arrow_of_time/pictures'

#for files that end with 1080-h264.png, change that port to .png
for filename in os.listdir(path):
    #add the root path
    if filename.endswith("1080-h264.png"):
        filename = path + "/" + filename
        print(filename)
        os.rename(filename, filename[:-13] + "png")