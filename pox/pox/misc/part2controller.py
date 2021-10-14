# Part 2 of UWCSE's Project 3
#
# based on Lab 4 from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class Firewall(object):
    """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """

    def __init__(self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # Switch Rules

        self.apply_icmp_flow_table_entry()

        self.apply_arp_flow_table_entry()

        self.drop_other_packets()

    def apply_icmp_flow_table_entry(self):
        # flow table entry for ICMP
        fm_icmp = of.ofp_flow_mod()  # To install a flow table entry
        # ICMP
        fm_icmp.priority = 10  # a reasonable priority, for overlapping entries, Higher values are higher priority
        fm_icmp.match.dl_type = 0x0800  # IPv4
        fm_icmp.match.nw_proto = 1  # ICMP   #IP PROTOCOL

        # flood all ports
        action = of.ofp_action_output(
            port=of.OFPP_FLOOD)  # Specify a switch port to tha you wish to send a packet out of it, also take
        # Various "Special" port numbers like flood that send from all of
        # port except that packet originally arrived on

        fm_icmp.actions.append(action)
        self.connection.send(fm_icmp)  # Send command (OpenFlow) message to the switch.

    def apply_arp_flow_table_entry(self):
        # flow table entry for ARP
        fm_arp = of.ofp_flow_mod()
        # ICMP
        fm_arp.priority = 9  # a reasonable priority
        fm_arp.match.dl_type = 0x0806  # ARP
        # flood all ports
        fm_arp.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(fm_arp)

    def drop_other_packets(self):
        # drop other packets
        fm_drop = of.ofp_flow_mod()
        # ICMP
        fm_drop.priority = 0  # a low priority
        # flood all ports
        self.connection.send(fm_drop)


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
    print("Unhandled packet :" + str(packet.dump()))


def launch():
    """
  Starts the component
  """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Firewall(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
