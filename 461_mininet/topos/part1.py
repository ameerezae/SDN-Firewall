#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

class part1_topo(Topo):
    
    def build(self):
        pass
        #switch1 = self.addSwitch('switchname')
        self.addSwitch('s1')
        for i in range(4):
            host_name = f'h{i+1}'
            self.addHost(host_name)
            self.addLink(host_name, 's1')
        #host1 = self.addHost('hostname')
        #self.addLink(hostname,switchname)

topos = {'part1' : part1_topo}

if __name__ == '__main__':
    t = part1_topo()
    net = Mininet (topo=t)
    net.start()
    CLI(net)
    net.stop()
