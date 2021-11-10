from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *


class SDNFirewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)

    def _handle_ConnectionUp(self, event):
        block = of.ofp_match()
        block.dl_type = 0x0800
        block.nw_src = "10.0.0.1"
        block.nw_dst = "10.0.0.2"
        block.nw_proto = 6
        block.tp_src = 80
        block.tp_dst = 5566
        flow_mod = of.ofp_flow_mod()
        flow_mod.match = block
        flow_mod.priority = 20
        event.connection.send(flow_mod)

        flow_mod_1 = of.ofp_flow_mod()
        flow_mod_1.priority = 10
        flow_mod_1.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))  # flood from all port
        event.connection.send(flow_mod_1)


def launch():
    core.registerNew(SDNFirewall)
