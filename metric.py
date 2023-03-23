from argparse import ArgumentParser
import os
import requests
import socket
import time
import pickle

#bootstrap
boot_ip = '192.168.1.2'
boot_port = '5000'
boot = False

#set the node's ip
name = socket.gethostname() 
ip = socket.gethostbyname(name)

def start():
    address = 'http://' + ip + ':' + str(port) + '/transaction'
    with open(file,'r') as f:
        for line in f:
            line = line.split()
            recipient = int(line[0][2])
            amount = int(line[1])
            string = {'id':recipient,'amount':amount}
            response = requests.post(address,json=string)
            if response.status_code == 200:
                print('Transaction completed')
            else:
                print('φελουρ')
                continue

if __name__ == "__main__":
    parser = ArgumentParser(description = "Metrics")
    parser.add_argument('-input',help='file to read')
    parser.add_argument('-p',type=int,help='port')
    parser.add_argument('-id',type=int,help='id')

    args = parser.parse_args()
    file = args.input
    port = args.p
    id = args.id

    file = os.path.join(file,'transactions'+str(id)+'.txt')

    start()

