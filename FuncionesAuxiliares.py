import numpy as np
from datetime import datetime


def cum_mean(arr):
    """Realiza el promedio acumulado"""
    cum_sum = np.cumsum(arr, axis=0)    
    for i in range(cum_sum.shape[0]):       
        if i == 0:
            continue
        cum_sum[i] =  cum_sum[i] / (i + 1)
    return cum_sum

