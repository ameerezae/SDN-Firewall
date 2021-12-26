from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import os

log = core.getLogger()
print(os.getcwd())



file = open('./policy.txt')
line = file.readline().split(' ')
first_device_ip = line[0]
first_device_server_port = int(line[1])
first_device_client_port = int(line[2])
second_device_ip = line[3]
second_device_server_port = int(line[4])
second_device_client_port = int(line[5])


class PolicyController(object):

    def __init__(self, connection):
        print(connection.dpid)
        self.connection = connection

        connection.addListeners(self)

        if connection.dpid == 1:
            self._table = {}
            self.allow = False

        else:
            print("UNKNOWN SWITCH")
            exit(1)

    def handle_ARP(self, event):
        fm = of.ofp_flow_mod()
        fm.priority = 33001
        fm.match.dl_type = 0x0806
        fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(fm)

    def _handle_ConnectionUp(self, event):
        self.handle_ARP(event)

    def _handle_PacketIn(self, event): # Packets not handled by the router rules will be forwarded to this method to be handled by the controller
        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        # packet_in = event.ofp  # The actual ofp_packet_in message.

        self._forward_to_switch(packet, event)

        print('Unhandled packet from ' + str(self.connection.dpid) + ':' + packet.dump())

    def _update(self, inport, packet): # learns port/MAC info, if new, otherwise, updates known
        src = packet.next.srcip
        if src in self._table and self._table[src] != (packet.src, inport):
            print(f"Re-learned {src}")
        elif src not in self._table:
            print(f"Learned {str(src)}")
        self._table[src] = (packet.src, inport)

    def _forward_to_switch(self, p, event):  # forward this packet to its destaination, and add to the flow table
        if not isinstance(p.next.dstip, IPAddr6):
            self._update(event.port, p)  # new knowledge?
        conn = event.connection
        me = conn.dpid
        if p.next.dstip in self._table:  # forward to dst?
            dest = p.next.dstip
            if isinstance(dest, IPAddr6):
                dest = self._find_by_port(event.port)
            dst = (self._table[dest][-1], self._table[dest][0])  # port, mac

            if dst[0] == event.port:  # through in-port?
                log.warning("Not sending packet back out of in-port " + str(event.port))
            else:
                do = [of.ofp_action_dl_addr.set_dst(dst[1]),  # MAC addr of dest
                      of.ofp_action_output(port=dst[0])]  # the port to dest
                want = of.ofp_match.from_packet(p, event.port)
                if p.next.srcip == first_device_ip and \
                        p.payload.payload.srcport == first_device_client_port and \
                        p.next.dstip == second_device_ip and \
                        p.payload.payload.dstport == second_device_server_port and \
                        self.allow == False:
                    print('################################################################# NOT ALLOWED')
                else:
                    conn.send(of.ofp_flow_mod(command=of.OFPFC_ADD,  # learn new rule
                                              idle_timeout=10,  # from l3learning.py
                                              hard_timeout=of.OFP_FLOW_PERMANENT,
                                              buffer_id=event.ofp.buffer_id,
                                              actions=do,
                                              match=want))
                    if p.next.srcip == second_device_ip and \
                            p.payload.payload.srcport == second_device_client_port and \
                            p.next.dstip == first_device_ip and \
                            p.payload.payload.dstport == first_device_server_port:
                        self.allow = True
                        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ALLOWED')
                    log.info('Added flow rule: traffic to ' + str(dest) + ' via ' + str(dst[0]))

            print('{a} forwarded packet from {b}>'.format(a=me, b=p.next.srcip) +
                  '{a}, using port {b}'.format(a=p.next.dstip, b=dst[0]))


def launch():

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        PolicyController(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
