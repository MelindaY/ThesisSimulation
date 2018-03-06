import os

if __name__ == "__main__":
    commands=[]
    i=0
    #while(i<1000):
    fname = "run.txt"
    with open(fname, 'r') as myfile:
        for command in myfile:
           commands.append(command)
    myfile.close()
    for command in commands:
        os.system(command)
