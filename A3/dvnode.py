import copy
from math import inf
from dvsim import Packet, NUM_NODES


class Node:
    """
    a node in the network
    """
    def __init__(self, nodeid: int, simulator):
        """
        Constructing a node in the network
        """
        self.nodeid = nodeid        # nodeid is the node number
        self.simulator = simulator
        # simulator is passed here so that the node can access 
        # - simulator.cost[nodeid] (only access the costs of this node's links) and
        # - simulator.to_link_layer() to send the message
        # You should not access anything else inside the simulator,

        # self.dist_table has the distance vectors as known by this node
        # It is an NxN matrix where N is NUM_NODES.
        # You need to make sure the dist_table is correctly updated throughout
        # the algorithm's execution.
        # Tip: although dist_table has N rows, each node might only access and
        # update a subset of the rows.
        self.dist_table = [[inf for _ in range(NUM_NODES)] for _ in range(NUM_NODES)]

        # self.predessor is a list of int
        # self.predecessor keeps a list of the predecessor of this node in the
        # path to each of the other nodes in the graph
        # You need to make sure this predecessors list is correctly updated
        # throughout the algorithm's execution
        self.predecessors = [None for _ in range(NUM_NODES)]

        # update node table row for self
        self.dist_table[self.nodeid] = self.simulator.cost[self.nodeid]

        # send packet to all neighbours
        self.neighbours = self.find_neighbours()

        vector = self.simulator.cost[self.nodeid]
        self.send_packet_to_neighbours(vector)

    def get_link_cost(self, other):
        """
        Get the cost of the link between this node and other.
        Note: This is the ONLY method that you're allowed use to get the cost of
        a link, i.e., do NOT access self.simulator.cost anywhere else in this
        class.
        DO NOT MODIFY THIS METHOD
        """
        return self.simulator.cost[self.nodeid][other]

    def get_dist_vector(self):
        """
        Get the distance vector of this node
        DO NOT MODIFY THIS METHOD
        """
        return self.dist_table[self.nodeid]

    def get_predecessor(self, other: int) -> int:
        """
        Get the predecessor of this node in the path to other
        DO NOT MODIFY THIS METHOD
        """
        return self.predecessors[other]

    def find_neighbours(self):
        """
        find neighbours from cost table
        inf col meaning not neighbours
        """
        neighbours = []
        cost_row = self.simulator.cost[self.nodeid]
        for i in range(NUM_NODES):
            if i != self.nodeid and cost_row[i] != inf:
                neighbours.append(i)
        return neighbours

    def send_packet_to_neighbours(self, vector):
        for i in self.neighbours:
            if i != self.nodeid and self.simulator.cost[self.nodeid][i] != inf:
                packet = Packet(self.nodeid, i, vector)
                self.simulator.to_link_layer(packet)

    def update(self, pkt: Packet):
        """
        Handle updates when a packet is received. May need to call
        self.simulator.to_link_layer() with new packets based upon what after
        the update. Be careful to construct the source and destination of the
        packet correctly. Read dvsim.py for more details about the potential
        errors.
        """
        if pkt.dest != self.nodeid:
            raise RuntimeError("packet that is not designed to sending to me")

        sender = pkt.src
        sender_vector = pkt.dist_vector
        self_vector = self.dist_table[self.nodeid]
        update_call = False

        # if sender row has at least one column smaller than current column
        for node in range(NUM_NODES):
            if sender_vector[node] < self.dist_table[sender][node]:
                update_call = True

        # copy sender's row to dis table
        self.dist_table[sender] = sender_vector

        # update row for self
        for node in self.neighbours:
            dp = sender_vector[node] + self_vector[sender]
            if dp < self_vector[node]:
                update_call = True
                self_vector[node] = dp

        # call link to layer if shorter path found
        if update_call:
            self.send_packet_to_neighbours(self_vector)

    def link_cost_change_handler(self, which_link: int, new_cost: int):
        """
        Handles the link-change event. The cost of the link between this node
        and which_link has been changed to new_cost. Need to update the
        information that is stored at this node, and notify the neighbours if
        necessary.
        """

        # TODO: implement this method
        pass

    def print_dist_table(self):
        """
        Prints the distance table stored at this node. Useful for debugging.
        DO NOT MODIFY THIS METHOD
        """
        print(" D{}|".format(self.nodeid).rjust(5), end="")
        for i in range(NUM_NODES):
            print("    {}".format(i), end="")
        print("\n----+{}".format("-----"*NUM_NODES))
        for i in range(NUM_NODES):
            print("{:4d}|".format(i), end="")
            for j in range(NUM_NODES):
                print(str(self.dist_table[i][j]).rjust(5), end="")
            print()
