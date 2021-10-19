# Part 3 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

log = core.getLogger()

# statically allocate a routing table for hosts
# MACs used in only in part 4
IPS = {
    "h10": ("10.0.1.10", '00:00:00:00:00:01'),
    "h20": ("10.0.2.20", '00:00:00:00:00:02'),
    "h30": ("10.0.3.30", '00:00:00:00:00:03'),
    "serv1": ("10.0.4.10", '00:00:00:00:00:04'),
    "hnotrust": ("172.16.10.100", '00:00:00:00:00:05'),
}


class Part3Controller(object):
    """
    A Connection object for that switch is passed to the __init__ function.
    """
    very_high_priority = 20
    high_priority = 10
    medium_priority = 5
    low_priority = 2
    very_low_priority = 1

    ipv4 = 0x0800

    def __init__(self, connection):
        print(connection.dpid)
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)
        # use the dpid to figure out what switch is being created
        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 21:
            self.cores21_setup()
        elif connection.dpid == 31:
            self.dcs31_setup()
        else:
            print("UNKNOWN SWITCH")
            exit(1)

    def flood_from_all_ports(self):
        flow_mod = of.ofp_flow_mod()
        flow_mod.priority = self.low_priority
        flow_mod.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))  # flood from all port
        self.connection.send(flow_mod)

    def drop_packet(self):
        flow_mod = of.ofp_flow_mod()
        flow_mod.priority = self.very_low_priority
        self.connection.send(flow_mod)

    def block_icmp_from_untrusted_host(self):
        flow_mod = of.ofp_flow_mod()
        flow_mod.priority = self.very_high_priority
        flow_mod.match.dl_type = self.ipv4
        flow_mod.match.nw_proto = 1                                             # ICMP
        flow_mod.match.nw_src = IPS['hnotrust'][0]
        # no action required and drop the packet
        self.connection.send(flow_mod)

    def block_ip_from_untrusted_host_to_data_center_through_cores21(self):
        flow_mod = of.ofp_flow_mod()
        flow_mod.priority = self.high_priority
        flow_mod.match.dl_type = self.ipv4
        flow_mod.match.nw_src = IPS['hnotrust'][0]
        flow_mod.match.nw_dst = IPS['serv1'][0]
        self.connection.send(flow_mod)

    def pass_ip_to_other_hosts_through_cores21(self, port, destination):
        flow_mod = of.ofp_flow_mod()
        flow_mod.priority = self.medium_priority
        flow_mod.match.dl_type = self.ipv4  # IPv4
        flow_mod.match.nw_dst = IPS[destination][0]  # to host 1
        flow_mod.actions.append(of.ofp_action_output(port=port))  # send it out through port 1
        self.connection.send(flow_mod)

    def pass_packet_out_of_subnet_through_cores21(self):
        flow_mod = of.ofp_flow_mod()
        flow_mod.priority = self.medium_priority
        flow_mod.match.dl_type = self.ipv4
        action = of.ofp_action_output(port=5)
        flow_mod.actions.append(action)
        self.connection.send(flow_mod)

    def s1_setup(self):
        # put switch 1 rules here
        self.flood_from_all_ports()

        self.drop_packet()

    def s2_setup(self):
        # put switch 2 rules here
        self.flood_from_all_ports()

        self.drop_packet()

    def s3_setup(self):
        # put switch 3 rules here
        self.flood_from_all_ports()

        self.drop_packet()

    def cores21_setup(self):
        # put core switch rules here
        self.block_icmp_from_untrusted_host()

        self.block_ip_from_untrusted_host_to_data_center_through_cores21()

        # Allow ip traffic to pass from cores21
        valid_hosts = ["h10", "h20", "h30", "serv1"]
        for port, destination in enumerate(valid_hosts):
            self.pass_ip_to_other_hosts_through_cores21(port=port+1, destination=destination)

        self.pass_packet_out_of_subnet_through_cores21()

        self.flood_from_all_ports()

        self.drop_packet()

    def dcs31_setup(self):
        # put datacenter switch rules here
        self.flood_from_all_ports()

        self.drop_packet()

    # used in part 4 to handle individual ARP packets
    # not needed for part 3 (USE RULES!)
    # causes the switch to output packet_in on out_port
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

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
        print("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())


def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Part3Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
