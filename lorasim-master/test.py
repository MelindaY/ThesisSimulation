import random
import numpy as np
import matplotlib.pyplot as plt
import sys
if __name__ == "__main__":
    # global ax
    # color = ['b']
    # plt.scatter(50, 100, c=color,s=256,alpha=0.3, marker='v')
    # for i in range(3):
    #     sf=i+10
    #     plt.scatter(random.random()*100, random.random()*100,color='orange', alpha=0.5)
    #
    # plt.savefig("a.svg")
    #
    # plt.show()
    # sys.stdin.read()
    # sys.stdin.close()

    nodes=[0,0,0,0,0,0,0]
    for i in range(0,6):
     nodes[i] = 852.5 + 7.8125 * random.randint(0, 16)
    print(nodes)