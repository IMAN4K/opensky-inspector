from multiprocessing import Pool
import os
from time import sleep  
import urllib  
  
def test(arg):
    print(arg)
    sleep(1)

with Pool(1) as pool:
    pool.map(test, range(20))