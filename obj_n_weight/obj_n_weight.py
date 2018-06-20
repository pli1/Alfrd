import sys
import os

def get_old_items():
    text=open("/home/pi/Alfrd/Output_old.txt")
    text_list=[]
    for line in text:
        text_list.append(line)
    return ','.join(text_list)

def get_new_items():
    text=open("/home/pi/Alfrd/Output.txt")
    text_list=[]
    for line in text:
        text_list.append(line)
    return ','.join(text_list)

def prepare_old_file():
    new=get_new_items()
    e=open('/home/pi/Alfrd/Output_old.txt',"w")
    e.write(new)
    e.close()
    return 0