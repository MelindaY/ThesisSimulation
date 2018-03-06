# -*- coding: utf-8 -*-
"""
 LoRaSim: simulate collisions in LoRa
 Copyright © 2016 Thiemo Voigt <thiemo@sics.se> and Martin Bor <m.bor@lancaster.ac.uk>

 This work is licensed under the Creative Commons Attribution 4.0
 International License. To view a copy of this license,
 visit http://creativecommons.org/licenses/by/4.0/.

 Do LoRa Low-Power Wide-Area Networks Scale? Martin Bor, Utz Roedig, Thiemo Voigt
 and Juan Alonso, MSWiM '16, http://dx.doi.org/10.1145/2988287.2989163

 $Date: 2016-10-17 13:23:52 +0100 (Mon, 17 Oct 2016) $
 $Revision: 218 $
"""

"""
 SYNOPSIS:
   ./loraDir.py <nodes> <avgsend> <experiment> <simtime> [collision]
 DESCRIPTION:
    nodes
        number of nodes to simulate
    avgsend
        average sending interval in milliseconds
    experiment
        experiment is an integer that determines with what radio settings the
        simulation is run. All nodes are configured with a fixed transmit power
        and a single transmit frequency, unless stated otherwise.
        0   use the settings with the the slowest datarate (SF12, BW125, CR4/8).
        1   similair to experiment 0, but use a random choice of 3 transmit
            frequencies.
        2   use the settings with the fastest data rate (SF6, BW500, CR4/5).
        3   optimise the setting per node based on the distance to the gateway.
        4   use the settings as defined in LoRaWAN (SF12, BW125, CR4/5).
        5   similair to experiment 3, but also optimises the transmit power.
    simtime
        total running time in milliseconds
    collision
        set to 1 to enable the full collision check, 0 to use a simplified check.
        With the simplified check, two messages collide when they arrive at the
        same time, on the same frequency and spreading factor. The full collision
        check considers the 'capture effect', whereby a collision of one or the
 OUTPUT
    The result of every simulation run will be appended to a file named expX.dat,
    whereby X is the experiment number. The file contains a space separated table
    of values for nodes, collisions, transmissions and total energy spent. The
    data file can be easily plotted using e.g. gnuplot.
"""
import win_unicode_console

win_unicode_console.enable()
import simpy
import random
import pandas as pd
import numpy as np
import math
import sys
from matplotlib import pyplot as plt
import os

# turn on/off graphics
graphics = 1

# do the full collision check
full_collision = False

# experiments:
# 0: packet with longest airtime, aloha-style experiment
# 0: one with 3 frequencies, 1 with 1 frequency
# 2: with shortest packets, still aloha-style
# 3: with shortest possible packets depending on distance



# this is an array with measured values for sensitivity
# see paper A study of LoRa, Table 1 sx1276
#              sf 125k 250k 500k
sf7 = np.array([7, -123, -120, -116])
sf8 = np.array([8, -126, -123, -119])
sf9 = np.array([9, -129, -125, -122])
sf10 = np.array([10, -132, -128, -125])
sf11 = np.array([11, -133, -130, -128])
sf12 = np.array([12, -136, -133, -130])


#
# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
#
# conditions for collions:
#     1. same sf
#     2. frequency, see function below (Martins email, not implementet yet):
def checkcollision(packet):
    col = 0  # flag needed since there might be several collisions for packet
    processing = 0
    global packetsAtBS
    for i in range(0, len(packetsAtBS)):
        if packetsAtBS[i].packet.processed == 1:
            processing = processing + 1
    if (processing > maxBSReceives):
        # print("too long: {}".format(len(packetsAtBS)))
        packet.processed = 0
    else:
        packet.processed = 1

    if packetsAtBS:
        # print("CHECK node {} (sf:{} bw:{} freq:{:.6e}) others: {}".format(
        #     packet.nodeid, packet.sf, packet.bw, packet.freq,
        #     len(packetsAtBS)))
        for other in packetsAtBS:
            if other.nodeid != packet.nodeid:
                # print(">> node {} (sf:{} bw:{} freq:{:.6e})".format(
                #     other.nodeid, other.packet.sf, other.packet.bw, other.packet.freq))
                # simple collision
                if frequencyCollision(packet, other.packet) \
                        and sfCollision(packet, other.packet):
                    if full_collision:
                        if timingCollision(packet, other.packet):
                            # check who collides in the power domain
                            c = powerCollision(packet, other.packet)
                            # mark all the collided packets
                            # either this one, the other one, or both
                            for p in c:
                                p.collided = 1
                        else:
                            # no timing collision, all fine
                            pass
                    else:
                        packet.collided = 1
                        other.packet.collided = 1  # other also got lost, if it wasn't lost already
                        col = 1
        return col
    return 0


#
# frequencyCollision, conditions
#
#        |f1-f2| <= 120 kHz if f1 or f2 has bw 500
#        |f1-f2| <= 60 kHz if f1 or f2 has bw 250
#        |f1-f2| <= 30 kHz if f1 or f2 has bw 125
def frequencyCollision(p1, p2):
    if (abs(p1.freq - p2.freq) <= 120 and (p1.bw == 500 or p2.freq == 500)):
        # print("frequency coll 500")
        return True
    elif (abs(p1.freq - p2.freq) <= 60 and (p1.bw == 250 or p2.freq == 250)):
       # print("frequency coll 250")
        return True
    else:
        if (abs(p1.freq - p2.freq) <= 30):
            # print("frequency coll 125")
            return True
            # else:
    #print("no frequency coll")
    return False


#
# sfCollision, conditions
#
#       sf1 == sf2
#
def sfCollision(p1, p2):
    if p1.sf == p2.sf:
        #print("collision sf node {} and node {}".format(p1.nodeid, p2.nodeid))
        # p2 may have been lost too, will be marked by other checks
        return True
    #print("no sf collision")
    return False


def powerCollision(p1, p2):
    powerThreshold = 6  # dB
    # print("pwr: node {0.nodeid} {0.rssi:3.2f} dBm node {1.nodeid} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(p1, p2,
    #                                                                                                            round(
    #                                                                                                                p1.rssi - p2.rssi,
    #                                                                                                                2)))
    if abs(p1.rssi - p2.rssi) < powerThreshold:
        # print("collision pwr both node {} and node {}".format(p1.nodeid, p2.nodeid))
        # packets are too close to each other, both collide
        # return both packets as casualties
        return (p1, p2)
    elif p1.rssi - p2.rssi < powerThreshold:
        # p2 overpowered p1, return p1 as casualty
        # print("collision pwr node {} overpowered node {}".format(p2.nodeid, p1.nodeid))
        return (p1,)
    # print("p1 wins, p2 lost")
    # p2 was the weaker packet, return it as a casualty
    return (p2,)


def timingCollision(p1, p2):
    # assuming p1 is the freshly arrived packet and this is the last check
    # we've already determined that p1 is a weak packet, so the only
    # way we can win is by being late enough (only the first n - 5 preamble symbols overlap)

    # assuming 8 preamble symbols
    Npream = 8

    # we can lose at most (Npream - 5) * Tsym of our preamble
    Tpreamb = 2 ** p1.sf / (1.0 * p1.bw) * (Npream - 5)

    # check whether p2 ends in p1's critical section
    p2_end = p2.addTime + p2.rectime
    p1_cs = env.now + Tpreamb
    # print("collision timing node {} ({},{},{}) node {} ({},{})".format(
    #     p1.nodeid, env.now - env.now, p1_cs - env.now, p1.rectime,
    #     p2.nodeid, p2.addTime - env.now, p2_end - env.now
    # ))
    if p1_cs < p2_end:
        # p1 collided with p2 and lost
        # print("not late enough")
        return True
    # print("saved by the preamble")
    return False


# this function computes the airtime of a packet
# according to LoraDesignGuide_STD.pdf
#
def airtime(sf, cr, pl, bw):
    H = 0  # implicit header disabled (H=0) or not (H=1)
    DE = 0  # low data rate optimization enabled (=1) or not (=0)
    Npream = 8  # number of preamble symbol (12.25  from Utz paper)

    if bw == 125 and sf in [11, 12]:
        # low data rate optimization mandated for BW125 with SF11 and SF12
        DE = 1
    if sf == 6:
        # can only have implicit header with SF6
        H = 1

    Tsym = (2.0 ** sf) / bw
    Tpream = (Npream + 4.25) * Tsym
    #print("sf", sf, " cr", cr, "pl", pl, "bw", bw)
    payloadSymbNB = 8 + max(math.ceil((8.0 * pl - 4.0 * sf + 28 + 16 - 20 * H) / (4.0 * (sf - 2 * DE))) * (cr + 4), 0)
    Tpayload = payloadSymbNB * Tsym
    return Tpream + Tpayload


# this is very complex prodecure for placing nodes
# and ensure minimum distance between each pair of nodes
def w_deploym_tofile(numNodes,nodes):
    fname = "data/" + "nodes" + str(numNodes) + ".txt"
    # if the file has been created,then return
    if os.path.isfile(fname):
        return
    while numNodes != 0:
        found = 0
        rounds = 0
        while (found == 0 and rounds < 100):
            a = random.random()
            b = random.random()
            if b < a:
                a, b = b, a
            posx = (b * maxDist * math.cos(2 * math.pi * a / b) + bsx)
            posy = (b * maxDist * math.sin(2 * math.pi * a / b) + bsy)
            if len(nodes) > 0:
                for index, n in enumerate(nodes):
                    dist = np.sqrt(((abs(n.x - posx)) ** 2) + ((abs(n.y - posy)) ** 2))
                    if dist >= 10:
                        found = 1
                        x = posx
                        y = posy
                    else:
                        rounds = rounds + 1
                        if rounds == 100:
                            print("could not place new node, giving up")
                            exit(-1)
            else:
                print("first node")
                x = posx
                y = posy
                found = 1
        res = str(x) + " " + str(y) + "\n"
        with open(fname, 'a') as myfile:
            myfile.write(res)
        numNodes -= 1
    myfile.close()


# this is very complex prodecure for placing nodes
# and ensure minimum distance between each pair of nodes
def my_deploy(numNodes,nodes):
    fname = "data/" + "nodes" + str(numNodes) + ".txt"
    # if the file has been created,then return
    if os.path.isfile(fname):
        return
    index = []
    while numNodes != 0:
        a = random.random()
        b = random.random()
        posx = math.cos(2 * math.pi * a) * maxDist*2 + maxDist*2
        posy = math.cos(2 * math.pi * b) * maxDist*2 + maxDist*5*2
        res = str(posx) + " " + str(posy) + "\n"
        with open(fname, 'a') as myfile:
            myfile.write(res)
        numNodes -= 1
    myfile.close()

# this function creates a node
#
class myNode():
    def __str__(self):
        return "["+str(self.nodeid)+"]"

    def __lt__(self, other):
        return self.packet.Prx > other.packet.Prx
    def __init__(self, nodeid, bs, period,packetlen):
        self.nodeid = nodeid
        self.period = period
        self.bs = bs
        self.x = 0
        self.y = 0#
# this function creates a packet (associated with a node)
# it also sets all parameters, currently random
#


def nodes_setting(nodes,packetlen):
    for node in nodes:
        node.dist = np.sqrt((node.x - bsx) * (node.x - bsx) + (node.y - bsy) * (node.y - bsy))
        node.packet = myPacket(node.nodeid, node.dist, packetlen)
        node.sent = 0


def color_nodes(nodes):
    # graphics for node
    nodes_7x = []
    nodes_7y = []
    nodes_8x = []
    nodes_8y = []
    nodes_9x = []
    nodes_9y = []
    nodes_10x = []
    nodes_10y = []
    nodes_11x = []
    nodes_11y = []
    nodes_12x = []
    nodes_12y = []
    nodes_color = ['blue', 'yellow', 'pink', 'orange', 'purple', 'brown']
    fig, ax = plt.subplots()
    ax.scatter(bsx, bsy, c='r', alpha=0.7, s=512, marker='>', edgecolors='none')
    for node in nodes:
        if node.packet.sf == 7:
            if node.x not in nodes_7x:
                nodes_7x.append(node.x)
                nodes_7y.append(node.y)
        if node.packet.sf == 8:
            nodes_8x.append(node.x)
            nodes_8y.append(node.y)
        if node.packet.sf == 9:
            nodes_9x.append(node.x)
            nodes_9y.append(node.y)
        if node.packet.sf == 10:
            nodes_10x.append(node.x)
            nodes_10y.append(node.y)
        if node.packet.sf == 11:
            nodes_11x.append(node.x)
            nodes_11y.append(node.y)
        if node.packet.sf == 12:
            nodes_12x.append(node.x)
            nodes_12y.append(node.y)
    scale = 50.0
    plt.scatter(nodes_7x, nodes_7y, alpha=0.6, s=scale, label='SF=7', color=nodes_color[0],
                edgecolors='none')
    ax.scatter(nodes_8x, nodes_8y, alpha=0.6, s=scale, label='SF=8', color=nodes_color[1],
               edgecolors='none')
    ax.scatter(nodes_9x, nodes_9y, alpha=0.6, s=scale, label='SF=9', color=nodes_color[2],
               edgecolors='none')
    ax.scatter(nodes_10x, nodes_10y, alpha=0.6, s=scale, label='SF=10', color=nodes_color[3],
               edgecolors='none')
    ax.scatter(nodes_11x, nodes_11y, alpha=0.6, s=scale, label='SF=11', color=nodes_color[4],
               edgecolors='none')
    ax.scatter(nodes_12x, nodes_12y, alpha=0.6, s=scale, label='SF=12', color=nodes_color[5],
               edgecolors='none')
    ax.legend()
    ax.grid(True)
    plt.title('Deployment')  # 显示图表标题
    plt.xlabel('Distance(m)')  # x轴名称
    plt.ylabel('Distance(m)')  # y轴名称
    plt.axis('tight')
    plt.savefig('imag/' + str(nrNodes) + 'nodes_' + 'experiment' + str(experiment) + '.png')
    #plt.show()


def nodes_deploy(nodes):
    fname = "data/" + "nodes" + str(len(nodes)) + ".txt"
    if os.path.isfile(fname) != True:
        print("deployment file doesn't exist!")
        exit(-1)
    with open(fname, 'r') as myfile:
        i = 0
        for deploy_xy in myfile:
            if (i >= len(nodes)):
                break
            x, y = deploy_xy.split()
            nodes[i].x = (float)(x)
            nodes[i].y = (float)(y)
            i += 1
    myfile.close()


class myPacket():
    global experiment
    global Ptx
    global gamma
    global d0
    global var
    global Lpld0
    global GL
    '''several find of settings:
               0,1:   one with 3 frequencies, 1 with 1 frequency
                 2:   with shortest packets, still aloha-style
             3,4,5:   with shortest possible packets depending on distance
                 6:   choose the fastest speed that available  function reset_sf
                 7:   random choose (random_set)
                 8:   use gateways to set,balance air_time and other issues
    '''
    def __init__(self, nodeid, distance, plen):

        self.nodeid = nodeid
        self.txpow = Ptx
        Prx = self.txpow  ## zero path loss by default
        self.rssi = Prx
        # randomize configuration values
        self.sf = 12
        self.cr = 1
        self.bw = 125
        #self.freq = 860000000 + random.randint(0, 2622950)
        self.freq = 852.5+7.8125*random.randint(0,16)
        #self.freq = 852.5
        # for experiment 3 find the best setting
        # OBS, some hardcoded values
        self.collided = 0
        self.processed = 0
        # log-shadow
        Lpl = Lpld0 + 10 * gamma * math.log(distance / d0)
        # print("Distance:", distance)
        # print("Lpl:", Lpl)
        self.Prx = self.txpow - GL - Lpl
        # for certain experiments override these
        if experiment == 1 or experiment == 0:
            self.sf = 8
            self.cr = 4
            self.bw = 125
            self.freq=915

        # for certain experiments override these
        if experiment == 2:
            self.sf = 7
            self.cr = 1
            self.bw = 500
        # lorawan
        if experiment == 4:
            self.sf = 12
            self.cr = 1
            self.bw = 125
        if (experiment == 3) or (experiment == 5):
            minairtime = 9999
            minsf = 0
            minbw = 0

            # print("Prx:", Prx)

            for i in range(0, 6):
                for j in range(1, 4):
                    if (sensi[i, j] < self.Prx):
                        self.sf = int(sensi[i, 0])
                        if j == 1:
                            self.bw = 125
                        elif j == 2:
                            self.bw = 250
                        else:
                            self.bw = 500
                        at = airtime(self.sf, 1, plen, self.bw)
                        if at < minairtime:
                            minairtime = at
                            minsf = self.sf
                            minbw = self.bw
                            minsensi = sensi[i, j]
            if (minairtime == 9999):
                print("does not reach base station")
                self.rssi=-11111
                return
            print("best sf:", minsf, " best bw: ", minbw, "best airtime:", minairtime)
            self.rectime = minairtime
            self.sf = minsf
            self.bw = minbw
            self.cr = 1

            if experiment == 5:
                # reduce the txpower if there's room left
                self.txpow = max(2, self.txpow - math.floor(self.Prx - minsensi))
                self.Prx = self.txpow - GL - Lpl
                print('minsesi {} best txpow {}'.format(minsensi, self.txpow))
        if experiment == 6:
            i = 5
            while i != -1:
                for j in range(1, 4):
                    sensi_node = sensi[i, j]
                    if self.Prx > sensi_node:
                        self.sf = i + 7
                        self.bw = 125 * pow(2,j-1)
                i-=1
            # if Prx < sensitivity:
            #     self.sf = 12
            self.cr = 1
        if experiment == 7:
            # randomize configuration values
            self.sf = random.randint(6, 12)
            self.cr = random.randint(1, 4)
            self.bw = random.choice([125, 250, 500])
            # for certain experiments override these and
            # choose some random frequences
            self.freq = random.choice([860000000, 864000000, 868000000])


    # this function resets sfs according to the distance, but the bw stays still.
    #  basic idea is to compare the receiver's sensitity to set the fastest rate that available
    def reset_sf(self):
        sensitivity = sensi[node.packet.sf - 7, [125, 250, 500].index(node.packet.bw) + 1]
        bw_index = [125, 250, 500].index(node.packet.bw) + 1
        # former_rssi = self.rssi
        for i in range(5, -1):
            if sensitivity < self.rssi:
                self.sf = i + 7
        if self.rssi < sensitivity:
            self.sf = 12
        self.cr = 1
        self.bw=125

    def random_set(self):
        # randomize configuration values
        self.sf = random.randint(6, 12)
        self.cr = random.randint(1, 4)
        self.bw = random.choice([125, 250, 500])

    def other_settings(self, plen):
        # transmission range, needs update XXX
        self.transRange = 150
        self.pl = plen
        self.symTime = (2.0 ** self.sf) / self.bw
        self.arriveTime = 0
        # print("frequency", self.freq, "symTime ", self.symTime)
        # print("bw", self.bw, "sf", self.sf, "cr", self.cr, "rssi", self.rssi)
        self.rectime = airtime(self.sf, self.cr, self.pl, self.bw)
        #print("rectime: ", self.rectime, " nodeid: ",self.nodeid )
        # denote if packet is collided



def total_fair_sf(nodes):
    ratio = np.array([0.44979919678714858, 0.25702811244979917, 0.14457831325301204, 0.080321285140562249,
                      0.044176706827309238, 0.024096385542168676])
    for i in range(0,len(ratio)):
        ratio[i] = ratio[i]*len(nodes)
    nodes.sort()
    k = 0
    for i in range(0,len(ratio)):
        if i > 0:
            k += int(ratio[i-1])
        for j in range(0, int(ratio[i])):
            if j+k < len(nodes):
                nodes[j+k].packet.sf = i+7


def is_fair_network(nodes):
    flag = True
    ratio = []
    part_ratio = []
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
    sf_number /= len(nodes)
    d = []
    for i in range(0, 7):
        d.append(sf_number[i]-ratio[i])
    i = 6
    sum_d = 0
    while i != 0:
        sum_d += d[i]
        if sum_d > 0:
            flag = False
        i -= 1
    flag = True
    if flag:
        total_fair_sf(nodes)
    else:
        Cb = []
        for i in range(0, 7):
            if d[i] > 0:
                Cb.append(i)
        # 分组
        k =0
        group = []
        alter = []
        for i in range(0,7):
            alter.append(i)
            if i == Cb[k]:
                group.append(np.array(alter))
                alter.clear()
                k += 1
        if len(alter) != 0:
            group.append(np.array(alter))
        for i in range(0, len(group)):
            if len(group[i]) > 1:
                total_sf = 0
                total_sf_fair = 0
                for j in range(0,len(group[i])):
                    total_sf += 7+group[i][j]/2**(7+group[i][j])
                    total_sf_fair += sf_number[group[i][j]]
                for j in range(1, len(group[i])):
                    current_ratio = (7 + group[i][j] / 2 ** (7 + group[i][j])) / total_sf
                    d[j] = abs(current_ratio * total_sf_fair - ratio[group[i][0]])
                    surplus = d[j]*len(nodes)
                    for k in range(0,surplus):
                        tmp_node = sf_number[group[i][0]].pop()
                        tmp_node.packet.sf = group[i][j]
                        sf_number[group[i][j]].append(tmp_node)


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
    print("Before assignment: ")
    for i in range(0,6):
        print(len(sf_number[i]))
    congestion_index = [0,0,0,0,0,0]
    for i in range(0, 6):
        congestion_index[i] = len(sf_number[i]) * timeonair_index[i]
    left = 0
    right = 5
    nsf = [0, 0, 0, 0, 0, 0]  # number of packets each SF should have orignal value: sf numbers
    for i in range(0,6):
        nsf[i] = len(sf_number[i])
    # average the number of different SFs
    print("congestion_index: ", congestion_index)
    while left < right:
        max_value = congestion_index[left]
        max_index = left
        for i in range(left, right+1):
            if congestion_index[i] > max_value:
                max_value = congestion_index[i]
                max_index = i
                break
        if (max_index == right & right-left == 1)| max_index == left:
            left += 1
        else:
            avg_congestion = 0
            for j in range(left,max_index):
                avg_congestion += congestion_index[j]
            avg_congestion /= (max_index-left)
            for j in range(left,max_index):
                nsf[j] = math.ceil(avg_congestion / timeonair_index[j])
                remove_number = len(sf_number[j]) \
                                - nsf[j]
                if remove_number > 2:
                    for k in range(0, remove_number):
                        if j+1<6:
                            tmp_node = sf_number[j].pop()
                            tmp_node.packet.sf += 1
                            sf_number[j + 1].append(tmp_node)
            left = max_index
    print("NSF: ",nsf)

# main discrete event loop, runs for each node
# a global list of packet being processed at the gateway
# is maintained
#
def transmit(env, node):
    while True:
        yield env.timeout(random.expovariate(1.0 / float(node.period)))
        # time sending and receiving
        # packet arrives -> add to base station
        node.sent = node.sent + 1
        if (node in packetsAtBS):
            print(len(packetsAtBS))
            #print(str(node.nodeid))
            #print("ERROR: packet already in")
        else:
            sensitivity = sensi[node.packet.sf - 7, [125, 250, 500].index(node.packet.bw) + 1]
            if node.packet.rssi < sensitivity:
                print("node {}: packet will be lost".format(node.nodeid))
                node.packet.lost = True
            else:
                node.packet.lost = False
                # adding packet if no collision
                if (checkcollision(node.packet) == 1):
                    node.packet.collided = 1
                else:
                    node.packet.collided = 0
                packetsAtBS.append(node)
                node.packet.addTime = env.now
        yield env.timeout(node.packet.rectime)
        if node.packet.lost:
            global nrLost
            nrLost += 1
        if node.packet.collided == 1:
            global nrCollisions
            global d_sfCollisions
            d_sfCollisions[node.packet.sf-7] +=1
            nrCollisions = nrCollisions + 1
        if node.packet.collided == 0 and not node.packet.lost:
            global nrReceived
            nrReceived = nrReceived + 1
        if node.packet.processed == 1:
            global nrProcessed
            nrProcessed = nrProcessed + 1

        # complete packet has been received by base station
        # can remove it
        if (node in packetsAtBS):
            packetsAtBS.remove(node)
            # reset the packet
        node.packet.collided = 0
        node.packet.processed = 0
        node.packet.lost = False


# global stuff
# Rnd = random.seed(12345)

nodes = []
packetsAtBS = []
env = simpy.Environment()

# maximum number of packets the BS can receive at the same time
maxBSReceives = 8

global nodes
global packetsAtBS
global env

# maximum number of packets the BS can receive at the same time
global maxBSReceives

# max distance: 300m in city, 3000 m outside (5 km Utz experiment)
# also more unit-disc like according to Utz
global bsId
global nrCollisions
global nrReceived
global nrProcessed
global nrLost

global Ptx
global gamma
global d0
global var
global Lpld0
global GL
global d_sfCollisions
global minsensi
# max distance: 300m in city, 3000 m outside (5 km Utz experiment)
# also more unit-disc like according to Utz
bsId = 1
nrCollisions = 0
nrReceived = 0
nrProcessed = 0
nrLost = 0

Ptx = 14
gamma = 2.08
d0 = 40.0
var = 0  # variance ignored for now
Lpld0 = 127.41
GL = 0

#
# "main" program
#

if __name__ == "__main__":

    d_sfCollisions = np.array([0, 0, 0, 0, 0, 0])
    nrSfNum = np.array([0, 0, 0, 0, 0, 0])
    nrSfReceived = np.array([0, 0, 0, 0, 0, 0])
    # get arguments
    if len(sys.argv) >= 5:
        nrNodes = int(sys.argv[1])
        avgSendTime = int(sys.argv[2])
        experiment = int(sys.argv[3])
        simtime = int(sys.argv[4])
        if len(sys.argv) > 5:
            full_collision = bool(int(sys.argv[5]))
        requirement=sys.argv[6]
        print("Nodes:", nrNodes)
        print("AvgSendTime (exp. distributed):", avgSendTime)
        print("Experiment: ", experiment)
        print("Simtime: ", simtime)
        print("Full Collision: ", full_collision)
    else:
        print("usage: ./loraDir nrNodes avgSendTime experimentNr simtime [full_collision]")
        print("experiment 0 and 1 use 1 frequency only")
        exit(-1)

    sensi = np.array([sf7, sf8, sf9, sf10, sf11, sf12])
    if experiment in [0, 1, 4, 7]:
        minsensi = sensi[5, 2]  # 5th row is SF12, 2nd column is BW125
    elif experiment == 2:
        minsensi = -112.0  # no experiments, so value from datasheet
    else:
        minsensi = np.amin(sensi)  ## Experiment 3 can use any setting, so take minimum
    Lpl = Ptx - minsensi
    print("amin", minsensi, "Lpl", Lpl)
    maxDist = d0 * (math.e ** ((Lpl - Lpld0) / (10.0 * gamma)))
    print("maxDist:", maxDist)

    # base station placement
    bsx = maxDist*2
    bsy = maxDist*2
    xmax = bsx + maxDist + 20
    ymax = bsy + maxDist + 20

    # prepare graphics and add sink
    # if (graphics == 1):
        # color = ['r']
        # ax.scatter(bsx, bsy, c=color, alpha=0.7, s=512,marker='>',edgecolors='none')
        # plt.ion()
        # plt.figure()
        # ax = plt.gcf().gca()
        # # XXX should be base station position
        # ax.add_artist(plt.Circle((bsx, bsy), 3, fill=True, color='green'))
        # ax.add_artist(plt.Circle((bsx, bsy), maxDist, fill=False, color='green'))


    for i in range(0, nrNodes):
        # myNode takes period (in ms), base station id packetlen (in Bytes)
        # 1000000 = 16 min
        node = myNode(i, bsId, avgSendTime, 10)
        nodes.append(node)
    # generate the file to deploy nodes
    my_deploy(nrNodes,nodes)
    #w_deploym_tofile(nrNodes, nodes)
    # use the file to deploy
    nodes_deploy(nodes)
    # set nodes parameters
    nodes_setting(nodes,20)
    if experiment ==8:
        total_fair_sf(nodes)
    for i in range(0,nrNodes):
         nodes[i].packet.other_settings(20)
    color_nodes(nodes)
    for i in range(0, nrNodes):
        env.process(transmit(env, nodes[i]))


    # start simulation

    env.run(until=simtime)

    # print stats and save into file
    print("nrCollisions ", nrCollisions)

    # compute energy
    # Transmit consumption in mA from -2 to +17 dBm
    TX = [22, 22, 22, 23,  # RFO/PA0: -2..1
          24, 24, 24, 25, 25, 25, 25, 26, 31, 32, 34, 35, 44,  # PA_BOOST/PA1: 2..14
          82, 85, 90,  # PA_BOOST/PA1: 15..17
          105, 115, 125]  # PA_BOOST/PA1+PA2: 18..20
    # mA = 90    # current draw for TX = 17 dBm
    V = 3.0  # voltage XXX
    sent = sum(n.sent for n in nodes)
    for node in nodes:
        nrSfNum[node.packet.sf-7] += node.sent
        if node.packet.collided == 0 and not node.packet.lost:
            nrSfReceived[node.packet.sf-7] += 1
    energy = sum(node.packet.rectime * TX[int(node.packet.txpow) + 2] * V * node.sent for node in nodes) / 1e6
    print("energy (in J): ", energy)
    print("sent packets: ", sent)
    print("collisions: ", nrCollisions)
    print("received packets: ", nrReceived)
    print("processed packets: ", nrProcessed)
    print("lost packets: ", nrLost)

    # data extraction rate
    der = (sent - nrCollisions) / float(sent)
    print("DER:", der)
    der = (nrReceived) / float(sent)
    print("DER method 2:", der)

    print("maxDist:", maxDist)
    # this can be done to keep graphics visible
    # if (graphics == 1):
    #     sys.stdin.read()
    print("different sf Packets: ", nrSfNum)
    print("different sf Collisions: ",d_sfCollisions)
    print("different sf Collisions Ratio: ",d_sfCollisions/nrSfNum)
    print("different sf Received: ", nrSfReceived)
    # save experiment data into a dat file that can be read by e.g. gnuplot
    # name of file would be:  exp0.dat for experiment 0
    fname = "data/"+"exp" + requirement+ ".dat"
    print(fname)
    if os.path.isfile(fname):
        res = "\n" + str(nrNodes) + "      " + str(nrCollisions/sent) + "      " + str(
            nrProcessed) + "      " + "      " \
              + str(nrReceived) + "   " + str(nrReceived * 20 / (simtime / 1000)) + "      " + str(
            energy) + "      " + str(der) + "      " \
              + str(experiment) + "      " + str(avgSendTime)
    else:
        res = "#nrNodes nrCollisions Transmission Processed Received Received Throughput OverallEnergy  DER ExperimentNumer SendDuration\n" + \
              str(nrNodes) + "      " + str(nrCollisions) + "/" + str(sent)+ "      " + str(nrProcessed)+ "      " + "      " \
              + str(nrReceived)+"   "+str(nrReceived*20/(simtime/1000)) + "      " + str(energy)+ "      "+str(der)+"      " \
              + str(experiment)+"      "+str(avgSendTime)
    with open(fname, 'a') as myfile:
        myfile.write(res)
    myfile.close()

    fname = "data/"+"latency_" + str(experiment)+"experiment"+ str(nrNodes)+"nodes" + ".dat"
    print(fname)
    for node in nodes:
        if os.path.isfile(fname):
            res = "\n" + str(node.packet.rectime)
        else:
            res = "#rectime\n" + str(node.packet.rectime)
        with open(fname, 'a') as myfile:
            myfile.write(res)
    myfile.close()

    # with open('nodes.txt','w') as nfile:
    #     for n in nodes:
    #         nfile.write("{} {} {}\n".format(n.x, n.y, n.nodeid))
    # with open('basestation.txt', 'w') as bfile:
    #     bfile.write("{} {} {}\n".format(bsx, bsy, 0))
