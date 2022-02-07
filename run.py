#!/usr/bin/python

import pandas as pd
import json
import os
import sys
import praw
import numpy as np
import itertools
import math
import networkx as nx
from matplotlib import pyplot as plt
from datetime import datetime
import time
import requests
import src.graph as graph
import src.draw_graph as draw_graph


def main(targets):
    if 'test' in targets:
        graph.generate_graphs([], test=True)
        draw_graph.draw('test_graph', size_ratio=1, test=True)
        
        
        
if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)