#!/usr/bin/python

"""
   Veicular Ad Hoc Networks - VANETs

"""

from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import random
import time
import json
import threading

car1_new=''
car2_new=''
car3_new=''
car4_new=''
def output(car1,car2,car3,car4):
    car_rssi={'car1':'','car2':'','car3':'','car4':''}
    threading.Timer(5.0, output,[car1,car2,car3,car4]).start()
    car1_new=str(car1.params['rssi'][0])
    car2_new=str(car2.params['rssi'][0])
    car3_new=str(car3.params['rssi'][0])
    car4_new=str(car4.params['rssi'][0])
    car_rssi.update({'car1':car1_new,'car2':car2_new,'car3':car3_new,'car4':car4_new})
    with open('rssi.json', 'w') as rssi:
        json.dump(car_rssi, rssi)
    os.system("scp -o StrictHostKeyChecking=no rssi.json lubuntu@192.168.56.107:/home/lubuntu/Workspace > scp_out.txt")


def topology():
    global car1_new
    global car2_new
    global car3_new
    global car4_new
    car1_new=''
    car2_new=''
    car3_new=''
    car4_new=''
    "Create a network."
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )

    print "*** Creating nodes"
    car = []
    stas = []
    for x in range(0, 4):
        car.append(x)
        stas.append(x)
    for x in range(0, 4):
        min = random.randint(20,40)
        max= random.randint(40,60)
        car[x] = net.addCar('car%s' % (x+1), wlans=1, ip='10.0.0.%s/8' % (x + 1), min_speed=min, max_speed=max, range=100)

    rsu11 = net.addAccessPoint( 'RSU11', ssid= 'RSU11', mode= 'g', channel= '1', range=200,ip='192.168.0.11' )
    rsu12 = net.addAccessPoint( 'RSU12', ssid= 'RSU12', mode= 'g', channel= '6', range=200,ip='192.168.0.12' )
    rsu13 = net.addAccessPoint( 'RSU13', ssid= 'RSU13', mode= 'g', channel= '11', range=200,ip='192.168.0.13' )
    rsu14 = net.addAccessPoint( 'RSU14', ssid= 'RSU14', mode= 'g', channel= '1', range=200,ip='192.168.0.14' )
    rsu15 = net.addAccessPoint( 'RSU15', ssid= 'RSU15', mode= 'g', channel= '6', range=200,ip='192.168.0.15' )
    c1 = net.addController( 'c1', controller=RemoteController, ip='192.168.56.107' )
    print "*** Configuring wifi nodes"
    net.configureWifiNodes()

    net.meshRouting('custom') 

    print "*** Associating and Creating links"
    net.addLink(rsu11, rsu12,bw=0.7,loss=2,delay='25ms')
    net.addLink(rsu12, rsu15,bw=1,loss=3,delay='10ms')
    net.addLink(rsu13, rsu15,bw=1,loss=2,delay='10ms')
    net.addLink(rsu13, rsu14,bw=5,loss=2,delay='5ms')
    net.addLink(rsu11, rsu14,bw=0.7,loss=8,delay='25ms')
    net.addLink(rsu11, rsu13,bw=0.7,loss=2,delay='25ms')
    net.addLink(rsu12, rsu14,bw=0.7,loss=8,delay='25ms')
    net.addLink(rsu11, rsu15,bw=0.7,loss=5,delay='25ms')
    net.addLink(rsu14, rsu15,bw=0.7,loss=6,delay='25ms')
    net.addLink(rsu12, rsu13,bw=5,loss=3,delay='5ms')
    print "*** Starting network"
    net.build()
    c1.start()
    rsu11.start( [c1] )
    rsu12.start( [c1] )
    rsu13.start( [c1] )
    rsu14.start( [c1] )
    rsu15.start( [c1] )
    i = 201
    for sw in net.vehicles:
        sw.start([c1])
        os.system('ifconfig %s 10.0.0.%s' % (sw, i))
        i+=1

    """uncomment to plot graph"""
    net.plotGraph(max_x=1000, max_y=1000)

    """Number of Roads"""
    net.roads(6)

    """Start Mobility"""
    net.startMobility(startTime=0)

    i = 1
    j = 2
    k = 1
    for c in car:
        c.cmd('ifconfig %s-wlan0 192.168.0.%s/24 up' % (c,k))
        c.cmd('ifconfig %s-eth0 192.168.1.%s/24 up' % (c,i))
        c.cmd('ip route add 10.0.0.0/8 via 192.168.1.%s' % j)
        i+=2
        j+=2
        k+=1

    i = 1
    j = 2
    for v in net.vehiclesSTA:
        v.cmd('ifconfig %s-eth0 192.168.1.%s/24 up' % (v, j))
        v.cmd('ifconfig %s-mp0 10.0.0.%s/24 up' % (v,i))
        v.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
        i+=1    
        j+=2

    for v1 in net.vehiclesSTA:
        i = 1
        j = 1
        for v2 in net.vehiclesSTA:
            if v1 != v2: 
                v1.cmd('route add -host 192.168.1.%s gw 10.0.0.%s' % (j,i))
            i+=1
            j+=2
    
    car1=car[0]
    car2=car[1]
    car3=car[2]
    car4=car[3]
    output(car1,car2,car3,car4)
    print "*** Running CLI"
    cmdcli= CLI(net)
    #cmdcli.do_px("print car1.cmd('iwconfig > 1234_py_test.txt')")
    #CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()
