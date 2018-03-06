import random
import numpy as np
import matplotlib.pyplot as plt
import os
import math

class myNode():
    def __init__(self):
        self.packet=myPacket()
        self.x=0
        self.y=0

    def __str__(self):
        return "["+str(self.x)+","+str(self.y)+"]"

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


def color_nodes(nodes):
    # graphics for node
    nodes_7x=[]
    nodes_7y = []
    nodes_8x = []
    nodes_8y = []
    nodes_9x = []
    nodes_9y = []
    nodes_10x = []
    nodes_10y = []
    nodes_11x = []
    nodes_11y = []
    nodes_12x= []
    nodes_12y = []
    nodes_color=['blue','yellow','pink','orange','purple','brown']
    fig, ax = plt.subplots()
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
    scale = 200.0
    plt.scatter( nodes_7x, nodes_7y, alpha=0.6, s=scale, label='SF=7', color=nodes_color[0],
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
    plt.show()
def w_deploym_tofile(numNodes,nodes):
    maxDist=50
    bsx=50
    bsy=50
    fname = "data/" + "nodes" + str(numNodes) + ".txt"
    # if the file has been created,then return
    if os.path.isfile(fname):
        return
    while numNodes!=0:
        found = 0
        rounds = 0
        while (found == 0 and rounds < 100):
            a = random.random()
            b = random.random()
            if b < a:
                a, b = b, a
            posx = b * maxDist * math.cos(2 * math.pi * a / b) + bsx
            posy = b * maxDist * math.sin(2 * math.pi * a / b) + bsy
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
        res = str(x) + " " + str(y)+"\n"
        with open(fname, 'a') as myfile:
            myfile.write(res)
        numNodes-=1
    myfile.close()

def nodes_deploy(nodes):
    fname = "data/" + "nodes" + str(len(nodes)) + ".txt"
    if os.path.isfile(fname) != True:
        print("deployment file doesn't exist!")
        exit(-1)
    with open(fname, 'r') as myfile:
        i = 0

        for deploy_xy in myfile:
            if(i>=len(nodes)):
                break
            x,y= deploy_xy.split()
            nodes[i].x = (float)(x)
            nodes[i].y = (float)(y)
            i+=1
    myfile.close()


if __name__ == "__main__":
    k = 0
    po = []
    while k<100:
        maxDist = 118.502866057
        bsx = maxDist+10
        bsy = maxDist + 10
        a = random.random()
        b = random.random()
        posx = math.cos(2 * math.pi * a) * maxDist + bsx*5
        po.append(posx)
        posy = math.cos(2 * math.pi * b) * maxDist + bsy*5
        print(posx,posy)
        k += 1
    print(np.array(po).mean())