"""some useful variables and functions"""

import sys
import linecache
import os
import pwd
import math
import traceback
from Levenshtein import distance


# check is it celery based running
if "worker" in sys.argv:
    celery = True
else:
    celery = False

# home path with celery based or not running:
if celery:
    home_dir = pwd.getpwuid(os.getuid()).pw_dir
else:
    home_dir = os.path.expanduser("~")


def dict_normalize(dictionary):
    dict_sum = 0
    for key in dictionary:
        val = dictionary[key]
        dict_sum += val * val
    dict_sum = math.sqrt(dict_sum)
    return {k: v / dict_sum for k, v in dictionary.items()}


def dict_scalar_multiply(dict1,dict2):
    multiply = 0
    for key in dict1:
        if key in dict2:
            multiply += dict1[key] * dict2[key]
    return multiply


def dict_sum(dict1,dict2):
    dictionary = dict1
    for key in dict2:
        if key in dictionary:
            dictionary[key] += dict2[key]
        else:
            dictionary[key] = dict2[key]
    return dictionary


def dict_multiply_to_scalar(dictionary,scalar):
    return {k: v*scalar for k, v in dictionary.items()}


def relative_file_path(file, path):
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file))) + '/' + path


def levenshtein_norm_distance(str1, str2):
    return distance(str1, str2) * 2 / float(len(str1) + len(str2))


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    print(traceback.format_exc())