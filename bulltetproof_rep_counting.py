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

ACCEL_UP = 1.05
ACCEL_DOWN = 0.95

while True:
    accel_sum_filt = float(input("acceleration: "))

    if accel_sum_filt > ACCEL_UP and (start_point or not stationary):
        moving_up = True
        moving_down = False
        up = False
        down = False
        stationary = False
        start_point = False
        print("moving up")

    if accel_sum_filt < ACCEL_DOWN and (start_point or not stationary):
        moving_up = False
        moving_down = True
        up = False
        down = False
        stationary = False
        start_point = False
        print("moving down")

    if accel_sum_filt < ACCEL_UP and accel_sum_filt > ACCEL_DOWN:
        stationary = True
        print("stationary")

    if stationary and (accel_sum_filt > ACCEL_UP or accel_sum_filt < ACCEL_DOWN) and (not moving_down and not moving_up):
        stationary = False
        if accel_sum_filt > ACCEL_UP:
            moving_up = True
            print("moving up")
        if accel_sum_filt < ACCEL_DOWN:
            moving_down = True
            print("moving down")

    if (moving_up or up) and stationary:
        moving_up = False
        moving_down = False
        up = True
        been_up = True
        print("up")
    
    if (moving_down or down) and stationary:
        moving_up = False
        moving_down = False
        down = True
        been_down = True
        print("down")

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