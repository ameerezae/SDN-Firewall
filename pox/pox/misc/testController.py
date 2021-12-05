# Part 4 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import pox.lib.packet as pkt

log = core.getLogger()


# statically allocate a routing table for hosts
# MACs used in only in part 4


class Part4Controller(object):
    """
  A Connection object for that switch is passed to the __init__ function.
  """

    def __init__(self, connection):
        print(connection.dpid)
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)
        # use the dpid to figure out what switch is being created
        if (connection.dpid == 1):
            self._table = {}
            self.allow = False

        else:
            print("UNKNOWN SWITCH")
            exit(1)

    def _handle_PacketIn(self, event):
        """
    Packets not handled by the router rules will be
    forwarded to this method to be handled by the controller
    """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.

        if self._is_arp(packet):  # handle ARP traffic?
            self._handle_ARP(packet, event)
        else:  # learn and forward?
            self._forward_to_switch(packet, event)

        # print('Unhandled packet from ' + str(self.connection.dpid) + ':' + packet.dump())

    # learns port/MAC info, if new, otherwise, updates known
    def _update(self, inport, packet, arp=False):
        if arp:
            src = packet.next.protosrc
        else:
            src = packet.next.srcip
        if src in self._table and self._table[src] != (packet.src, inport):
            print(f"Re-learned {src}")  # update info
        elif src not in self._table:
            print(f"Learned {str(src)}")  # new dst to learn
        self._table[src] = (packet.src, inport)
        print(self._table)

    def _is_arp(self, p):
        return p.type == p.ARP_TYPE

    def _handle_ARP(self, p, event):
        a = p.next
        msg = 'request' if a.opcode == 1 else 'reply'
        print(f"Got ARP {msg} from {str(a.protosrc)} to {str(a.protodst)}")
        self._update(event.port, p, arp=True)
        self._reply(p, event)

    def _reply(self, p, event):
        me = event.connection.dpid
        a = p.next
        r = pkt.arp()
        r.hwtype = a.hwtype
        r.prototype = a.prototype
        r.hwlen = a.hwlen
        r.protolen = a.protolen
        r.opcode = pkt.arp.REPLY
        r.hwdst = a.hwsrc
        r.protodst = a.protosrc
        r.protosrc = a.protodst
        r.hwsrc = p.src
        e = pkt.ethernet(type=p.type, src=self.
                         dpid_to_mac(me), dst=a.hwsrc)
        e.set_payload(r)
        msg = of.ofp_packet_out()
        msg.data = e.pack()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
        msg.in_port = event.port
        event.connection.send(msg)
        print("Replied to ARP request for " + str(r.protosrc))

    def dpid_to_mac(self, dpid):
        return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))

    # forward this packet to its destaination, and add to the flow table
    def _forward_to_switch(self, p, event):
        log.debug('HEEEEEE: ' + str(p.next.dstip))
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
                if p.next.srcip == "10.0.0.1" and p.next.dstip == "10.0.0.2" and self.allow == False:
                    print('cant')
                else:
                    conn.send(of.ofp_flow_mod(command=of.OFPFC_ADD,  # learn new rule
                                              idle_timeout=10,  # from l3learning.py
                                              hard_timeout=of.OFP_FLOW_PERMANENT,
                                              buffer_id=event.ofp.buffer_id,
                                              actions=do,
                                              match=want))
                    if p.next.srcip == "10.0.0.2" and p.next.dstip == "10.0.0.1":
                        self.allow = True
                    log.info('Added flow rule: traffic to ' + str(dest) + ' via ' + str(dst[0]))

            print('{a} forwarded packet from {b}>'.format(a=me, b=p.next.srcip) +
                  '{a}, using port {b}'.format(a=p.next.dstip, b=dst[0]))


def launch():
    """
  Starts the component
  """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Part4Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
