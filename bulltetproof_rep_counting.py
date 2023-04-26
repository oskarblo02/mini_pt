import time
import numpy as np

accel_sum_filt = 0

rep_count = 0
rep_time = np.zeros(1000)
up_time = np.zeros(1000)
down_time = np.zeros(1000)
time_start = 0
moving_up = False
moving_down = False
up = False
down = False
been_down = False
been_up = False
stationary = True
start_point = True
check_up = False
check_down = False
high = 0
low = 0

ACCEL_UP = 1.05
ACCEL_DOWN = 0.95

while True:
    accel_sum_filt = float(input("acceleration: "))

    if accel_sum_filt > ACCEL_UP and high == 0:
        moving_up = True
        stationary = False
        high  = 1
    if accel_sum_filt < ACCEL_UP and high == 1:
        high  = 2
    if accel_sum_filt < ACCEL_DOWN and high == 2:
        high  = 3
    if accel_sum_filt > ACCEL_DOWN and high == 3:
        high = 4
    if accel_sum_filt < ACCEL_UP and accel_sum_filt > ACCEL_DOWN and high == 4:
        stationary = True
        up = True
        been_up == True
        moving_up = False
        high = 0

    if accel_sum_filt < ACCEL_DOWN and low == 0:
        moving_down = True
        stationary = False
        low  = 1
    if accel_sum_filt > ACCEL_DOWN and low == 1:
        low  = 2
    if accel_sum_filt > ACCEL_UP and low == 2:
        low  = 3
    if accel_sum_filt < ACCEL_UP and low == 3:
        low = 4
    if accel_sum_filt < ACCEL_UP and accel_sum_filt > ACCEL_DOWN and low == 4:
        stationary = True
        down = True
        been_down = True
        moving_down = False
        low = 0

    if moving_down:
        time_start = time.time()
        down = False
        up = False
        stationary = False

    if moving_up:
        time_start = time.time()
        down = False
        up = False
        stationary = False

    if up and not check_up:
        up_time[rep_count] = time.time() - time_start
        check_up = True
    
    if down and not check_down:
        down_time[rep_count] = time.time() - time_start
        check_down = True
    
    if been_down and been_up:
        rep_time[rep_count] = down_time[rep_count] + up_time[rep_count]
        been_up = False
        been_down = False
        check_down = False
        check_up = False
        start_point = True
        rep_count +=1

    print("high         ", high)
    print("low          ", low)
    print("stationary   ", stationary)
    print("moving up    ", moving_up)
    print("moving dowwn ", moving_down)
    print("up           ", up)
    print("down         ", down)
    print("been up      ", been_up)
    print("been down    ", been_down)
    print("start point  ", start_point)
    print("check up     ", check_up)
    print("check down   ", check_down)
    print("rep count    ", rep_count)
    print("up time      ", round(up_time[rep_count], 2))
    print("down time    ", round(down_time[rep_count], 2))
    if rep_count >0:
        print("up time      ", round(up_time[rep_count-1], 2))
        print("down time    ", round(down_time[rep_count-1], 2))
        print("rep time     ", round(rep_time[rep_count-1], 2))


    for i in range(rep_count):
        print("reps:        ", i+1)
        print("rep time:    ", round(rep_time[i], 2))
        print("down time:   ", round(down_time[i], 2))
        print("up time:     ", round(up_time[i], 2))
