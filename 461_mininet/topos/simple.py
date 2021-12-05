from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def SimpleTopo():
    net = Mininet(controller=RemoteController)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost( 'h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01' )
    h2 = net.addHost( 'h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02' )
    h3 = net.addHost( 'h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03' )


    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')


    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    info('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    SimpleTopo()