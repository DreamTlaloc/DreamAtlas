# Importing dependencies
import math                                 # Critical
import os                                   # Critical
import pathlib                              # Critical
import struct                               # Critical
import ctypes                               # Not sure
import matplotlib as mpl                    # Optional
import matplotlib.cm as cm                  # Optional
import matplotlib.pyplot as plt             # Optional
import numpy as np                          # Critical
import scipy as sc                          # Divest
import scipy.cluster.vq as sccvq
import random as rd                         # Divest
import networkx as ntx                      # Divest
import minorminer as mnm                    # Divest
import tkinter.filedialog as tkf            # Critical
import ttkbootstrap as ttk                  # Critical
from ttkbootstrap.constants import *        # Critical
from ttkbootstrap.tooltip import ToolTip    # Critical
from numba import njit, prange              # Critical
from copy import copy                       # Critical
from PIL import ImageShow, ImageTk, Image   # Critical
import time                                 # Testing
import cProfile                             # Testing


# Importing classes and functions at the end avoids circular dependencies
from DreamAtlas.databases import *
from DreamAtlas.functions import *
from DreamAtlas.classes import *
from DreamAtlas.generators import generator_dreamatlas
from DreamAtlas.GUI import run_interface
