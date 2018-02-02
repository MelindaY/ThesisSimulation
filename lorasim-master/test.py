import random
import numpy as np
import matplotlib.pyplot as plt
import os
import math

class myNode():
    def __init__(self):
        self.packet=myPacket()


class myPacket():
    def __init__(self):
        self.sf = random.choice([7, 8, 9, 10, 11, 12])


def scheduleSF(nodes):
    timeonair_index = [65.536, 118.784, 217.088, 401.408, 753.664, 1409.024]
    node_sf7 = []
    node_sf8 = []
    node_sf9 = []
    node_sf10 = []
    node_sf11 = []
    node_sf12 = []
    ## 2-deminsional array to store the nodes with same sf
    sf_number = []
    sf_number.append(node_sf7)
    sf_number.append(node_sf8)
    sf_number.append(node_sf9)
    sf_number.append(node_sf10)
    sf_number.append(node_sf11)
    sf_number.append(node_sf12)

    for node in nodes:
        sf_number[node.packet.sf - 7].append(node)
    congestion_index = [0, 0, 0, 0, 0, 0]
    for i in range(0, 6):
        congestion_index[i] = len(sf_number[i]) * timeonair_index[i]
    left = 0
    right = 6
    nsf = [0, 0, 0, 0, 0, 0]  # number of packets each SF should have
    # average the number of different SFs
    while left != right:
        print("left:", left, "right: ", right)
        max_value = congestion_index[left]
        max_index = left
        for i in range(left, right):
            if congestion_index[i] > max_value:
                max_value = congestion_index[i]
                max_index = i
        if max_index == right:
            right -= 1
        else:
            avg_congestion = 0
            for j in range(max_index, right):
                avg_congestion += congestion_index[j]
            print("max_index:", max_index, "right:", right)
            avg_congestion /= (right - max_index + 1)
            for j in range(max_index, right):
                nsf[j] = (int)(avg_congestion / timeonair_index[j])
                remove_number = len(sf_number[j]) \
                                - nsf[j]
                if remove_number > 2:
                    for k in range(0, remove_number):
                        if j + 1 < 6:
                            tmp_node = sf_number[j].pop()
                            tmp_node.packet.sf += 1
                            sf_number[j + 1].append(tmp_node)
            left = max_index + 1

def w_deploym_tofile(numNodes):
    maxDist=100
    bsx=50
    bsy=50
    fname = "data/" + "nodes" + str(numNodes) + ".txt"
    while numNodes!=0:
        a = random.random()
        b = random.random()
        if b < a:
            a, b = b, a
        posx = b * maxDist * math.cos(2 * math.pi * a / b) + bsx
        posy = b * maxDist * math.sin(2 * math.pi * a / b) + bsy
        x = posx
        y = posy
        res = str(x) + " " + str(y)+"\n"
        with open(fname, 'a') as myfile:
            myfile.write(res)
        numNodes-=1
    myfile.close()

if __name__ == "__main__":
    w_deploym_tofile(100)
