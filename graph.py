#------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      GeoffB
#
# Created:     31/12/2014
# Copyright:   (c) GeoffB 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import collections
import math
from itertools import groupby


def flatten_coords(coords, imwidth):

    xcoord, ycoord = coords
    number_to_the_start_of_row = ycoord * imwidth
    flat_value = number_to_the_start_of_row + xcoord
    return flat_value


def get_cid_from_bid(graph, bid):

    """If you only have a branch id send that into get_cid_from_bid and search
    the cluster_dict and return the cluster id that contains that branch id"""

    check = []

    kokey = graph.cluster_dict.keys()
    for item in kokey:
        if bid in graph.cluster_dict[item].keys():
            return item
    return check



def calc_euclid_dist(a, b, round=0, signed=0):

    """takes two coordinates a and b and gets the distance between
    them using a**2 + b**2 = c**. Rounding is optional set it to 1 to send
    raw distance."""

    x, y = a
    xd, yd = b
    if a == b:
        return 1
    else:
        distance_squared = abs(x-xd)**2 + abs(y-yd)**2
        distance = math.sqrt(distance_squared)

    if round == 0:
        return int(distance)
    else:
        return distance


def get_cluster_size(cluster, cid):

    """counts the number of pixels in a cluster. Used to capture small
    clusters that can be reintegrated into the large drawing ecosystem."""

    summed_len = 0
    branch_keys = cluster[cid].keys()

    for branch in branch_keys:
        branch_node_list = cluster[cid][branch]
        for node in branch_node_list:
            try:
                summed_len += len(node.flat_children)
            except:
                summed_len += 1
    return summed_len




def unpack_coords(flat_value, width):

    """Convert the matrix integer or flat_value into its coordinate pair.
    Should only be used with non-node values. Nodes have their one fuction
    unpackCoords"""

    # this rounds the y value which makes the x value a whole number as well
    y = flat_value/width
    x = abs((y*width)-flat_value)
    return x, y


class Point:

    """Store a flat value representation of the x,y coords of a pixel location.
    Attributes include, flat_value, forwards and backwards direction, point
    classification. Its only method is that it needs to return itself in
    unpacked form"""

    width = 0

    # flat_value = matrix location
    # angle list = list of arcs in circle
    # classification is number of penetrations

    def __init__(self, flat_value, angle_list, angle_spans, origin_dist):
        self.flat_value = flat_value
        self.angle_list = angle_list
        self.angle_spans = [span[0] for span in angle_spans]
        self.avg_chord_coords = [coord[1] for coord in angle_spans]
        self.origin_dist = origin_dist

    @property
    def unpack_coords(self):

        """unpackCoords converts the flat values found in the cluster dict
        to thier appropriate coordinate pair.

        Usage:  node.unpackCoords

        """

        y = self.flat_value/Point.width
        x = abs((y * self.width) - self.flat_value)
        return x, y

    @property
    def term_span_quality(self):
        """
        Only used with term
        :return:
        """
        return self.angle_spans

    @property
    def span_quality(self):

        """This will have to be adjusted to account for singeltons, and doubles
        """

        total_seq_differnce = sum([abs(span - self.angle_spans[i - 1]) for i, span in enumerate(self.angle_spans)][1:])
        return total_seq_differnce

    def span_equality(self, span=10):

        """Find out the difference between the angle_spans. If the max
        difference is too large its a not a clean example."""

        # how far away are we from average?? NO  100 39 29 10   178/4 45
        #  39 43 40 28  #compactness  #sort them and get the median
        if len(self.angle_list) == 4:  #terms
            angle_max = max(self.angle_spans)

            if angle_max <= 35:  #24 for flange
                ordered_spans = sorted(self.angle_spans)
                mid_one, mid_two = ordered_spans[1:3]
                median = int((mid_one + mid_two)/float(2))

                span_difs = [abs(suk - median) for suk in self.angle_spans]
                spans_over_threshold = [tuk for tuk in span_difs if tuk >= span]

                if spans_over_threshold:
                    return 0
                else:
                    return 1
            else:
                return 0

    @property
    def num_penetrations(self):

        penetrations = len(self.angle_list)
        return penetrations

    @property
    def angle_span(self):

        """angle_span used only with two penetration lists"""
        try:
            angle_one, angle_two = self.angle_list
            dif = abs(angle_one - angle_two)
            if dif > 180:
                dif -= 360
            return dif
        except:
            return -1


class Node:

    """Node class holds a line of Point class pixels that are connected
    horizontally. Node is the primary means of building the graph of the
    drawing.

        cluster_id: The cluster which the node belongs
        parent: Tuple, list or node representing the parent of the node
        children: The Point class pixels residing in the node
        line_count: What y value the node resides
        layer: Attribute that allows the node be linked agraphically to others

        Node.unpackChildren returns the flat values grouped in the node"""

    def __init__(self, cluster_id, branch_id, parent, line_count, children=[], layer=0):

        """

        Args:
            cluster_id:
            branch_id:
            parent:
            line_count:
            children:
            layer:

        Returns:

        """

        # self.point_list = point_list
        self.cluster_id = cluster_id
        self.branch_id = branch_id
        self.parent = parent
        self.children = children
        self.line_count = line_count
        self.layer = layer

        try:
            start_child = self.children.unpack_coords
            self.width = 1
        except:
            start_child = self.children[0].unpack_coords
            end_child = self.children[-1].unpack_coords
            self.width = calc_euclid_dist(start_child, end_child)

        try:
            self.flat_children = self.children.flat_value
        except:
            self.flat_children = [x.flat_value for x in self.children]

        try:
            children_in_points = [milf.unpack_coords for milf in self.children]
        except:
            children_in_points = self.children.unpack_coords

        if type(self.children) == list:
            start = children_in_points[0]
            end = children_in_points[-1]
            x, y = start
            xd, yd = end
            xavg = int(abs(x + xd)/float(2))
            yavg = int(abs(y + yd)/float(2))
            coords = xavg, yavg
            self.skeleton_point = coords
        else:
            self.skeleton_point = children_in_points

    @property
    def unpack_children(self):
        try:
            coordinate_children = [child.unpack_coords for child in self.children]
        except:
            coordinate_children = [self.children.unpack_coords]  # lisitfy single
        if coordinate_children:
            return coordinate_children
        else:
            print coordinate_children, 'this is what happend'
            return

    def get_penetration_indexes(self, num_penetrations):

        """save the indexes"""

        child_points = self.children
        save_indexes = []
        if type(child_points) == list:
            for point in child_points:
                if point.num_penetrations == num_penetrations:
                    index = child_points.index(point)
                    save_indexes.append(index)
        else:
            if child_points.num_penetrations == num_penetrations:
                save_indexes.append(0)
        if save_indexes:
            return save_indexes

    def report_num_terminations(self):

        total_num_terminations = 0
        child_points_in_node = self.children
        try:
            for point in child_points_in_node:
                penetration_count = point.num_penetrations
                if penetration_count == 1:
                    total_num_terminations += penetration_count
        except:
            penetration_count = child_points_in_node.num_penetrations
            if penetration_count == 1:
                total_num_terminations = 1

        return total_num_terminations

    def report_num_penetrations(self, num_pens):

        total_num_terminations = 0
        child_points_in_node = self.children
        try:
            for point in child_points_in_node:
                penetration_count = point.num_penetrations
                if penetration_count == num_pens:
                    total_num_terminations += penetration_count
        except:
            penetration_count = child_points_in_node.num_penetrations
            if penetration_count == 1:
                total_num_terminations = 1

        return total_num_terminations


class Graph:

    """Container and methods to keep track of the nodes. Also contains methods
    to create and add branches and clusters.

    cluster_dict is a default dictionary of dictionarys.
    cluster_dict.keys() is a list of clusters found in the drawing
    cluster_dict[cid].keys() is a list of branches found in the cluster

        AddNode() creates and initializes a Node instance.
        MostRecent() get possible parents of a single child, used with GetLast
        CreateAddNode() inserts a node into a branch below last inserted node.
        GetLastGen() gets the possible parents of the current children
        CreateClusterNode() creates a new cluster with an orphan node"""

    # default dict is used to load dictionary values without checking
    cluster_dict = collections.defaultdict(dict)
    closed_keys = []
    lame_duck_parents = []

    def __init__(self, im_width, im_height):
        self.im_width = im_width
        self.im_height = im_height

    @classmethod
    def add_node(cls, cluster_id, branch_id, node):
        """This adds a node to a branch. It either appends the new node to
        the existing list or simply adds it if there is no list"""

        try:    # try to pull the node list out

            node_list = cls.cluster_dict[cluster_id][branch_id]

            if node not in node_list:
                node_list.append(node)
                cls.cluster_dict[cluster_id][branch_id]= node_list

        except:  # if no node list exists then just add
            cls.cluster_dict[cluster_id][branch_id] = [node]

    @classmethod
    def MostRecent(cls, cluster_id, bkey, line):

        """Get the last node's line number if the number
        is greater than 8 more than the last one we have
        no new parents and thus create a new cluster otherwise
        just return the line level"""

        node_list = cls.cluster_dict[cluster_id][bkey]

        if node_list[-1].line_count + 10 <= line:  # was 8, 9 made no change

            # add this branch id to the closed bid keys list
            bid = node_list[0].branch_id
            cls.closed_keys.append(bid)
        else:

            return node_list[-1]

    @classmethod
    def createAddNode(Graph, child_father, fathers_interface, line_num, raw_points):

        """Create the node by adding the point class instances and add it
        to the last thing"""

        if type(child_father[0])== tuple:  # get the child
            child_list_flat = list(child_father[0])[0]  # get the child list
        else:

            child_list_flat = child_father[0]

        for point_class_list in raw_points:  # get children in Point class form

            if isinstance(point_class_list, Point):
                if child_list_flat == point_class_list.flat_value:
                    child_list = point_class_list
            else:
                if child_list_flat == [x.flat_value for x in point_class_list]:
                    child_list = point_class_list

        father_id = child_father[1]  # get the parent list
        father_node = ([x for x in fathers_interface
                        if x.flat_children == father_id][0])

        bid = father_node.branch_id
        cid = father_node.cluster_id

        # call the Node class to create the instance then AddNode to branch
        new_child_node = Node(cid, bid, father_node, line_num, child_list)
        Graph.add_node(cid, bid, new_child_node)

    def get_last_gen(Graph, current_line):

        """getLastGen retrieves a list of the last line of possible fathers.
        These fathers will then be tested against the new children for
        paternity"""

        last_generation = []
        # saved_roots = []
        cluster_keys = Graph.cluster_dict.keys()

        for ckey in cluster_keys:

            branch_keys = Graph.cluster_dict[ckey].keys()  #keys for branch

            if len(branch_keys) == 1:
                if ckey not in Graph.closed_keys:
                    interface = Graph.MostRecent(ckey, branch_keys[0], current_line)
                    if interface and interface not in last_generation:
                        last_generation.append(interface)
            else:
                for bkeys in branch_keys:
                    if bkeys not in Graph.closed_keys:

                        interface = Graph.MostRecent(ckey, bkeys, current_line)
                        if interface and interface not in last_generation:
                            last_generation.append(interface)

        if last_generation:
            return last_generation
        else:
            return 0

    def create_cluster_branch(self, orphan, line_num):  # create cluster

        """If we find orphans then we create a new node out of the point
        class objects and insert it into the cluster dictionary at the top
        level we send in a node already. The node's parent points to itself
        as its cluster_id that's how we know its a cluster later when
        assembling the drawing"""

        try:
            cluster_id = orphan.flat_value
        except:
            cluster_id = tuple([x.flat_value for x in orphan])

        # create a node instance and add it to the graph
        orphan_node = Node(cluster_id, cluster_id, cluster_id, line_num, orphan)
        Graph.cluster_dict[cluster_id][cluster_id] = [orphan_node]

    def create_merge_branch(self, cid, merge_child, occluded_parents, fathers, line_num, point_list):

        """create a new branch that merges the clusters of two or more branches
        that have different clusters"""

        saved_parent_nodes = []

        for oparent in occluded_parents:

            parent_node = [pnode for pnode in fathers if pnode.flat_children == oparent][0]
            parent_node.cluster_id = cid  # !!!!!!!!!! Questionable cid change??

            if parent_node not in saved_parent_nodes:
                saved_parent_nodes.append(parent_node)

        for node_points in point_list:  # get the children in Point class form
            try:
                flat_children = [cpoint.flat_value for cpoint in node_points]
            except:
                flat_children = node_points.flat_value

            if merge_child == flat_children:
                child_points = node_points
                break

        if type(merge_child) == list:
            merge_child = tuple(merge_child)  # tupleate the bid if necessary

        merge_node = Node(cid, merge_child, saved_parent_nodes, line_num, child_points)
        Graph.add_node(cid, merge_child, merge_node)  # start itself

        for par in saved_parent_nodes:
            bra_id = par.branch_id
            if bra_id not in Graph.closed_keys:
                Graph.closed_keys.append(bra_id)

        return merge_node

    def create_branch_node(self, cid, child, parents, line_num, child_points):

        # i need to get the cluster id, turn the child into a branch id, then
        # create a node then insert it into the cluster its unparented?? No
        # it will be parented by all parents

        # create the branch_id
        if type(child) == list:
            child_bid = tuple(child)
        else:
            child_bid = child

        for cpoint in child_points:  # get the individual child points from the node
            try:
                test_points = [point.flat_value for point in cpoint]
            except:
                test_points = cpoint.flat_value
            if test_points == child:
                children = cpoint

        # create the node
        open_node = Node(cid, child_bid, parents, line_num, children)
        Graph.add_node(cid, child_bid, open_node)

    def create_split_branch(self, cid, child_father, father_node, line_num, point_list, lame_parent=0):

        """In order to use this it must be part of a cluster already. This is
        used in splits or merges to create a new branch and close the old ones
        Do we create a father less node??"""

        child, parent = child_father
        cid_father = father_node.cluster_id
        bid_father = father_node.branch_id

        # create the new branch key from the flat child value
        if type(child)==int:  # if its an int
            new_branch_id = child
        else:
            new_branch_id = tuple(child)  # keys must be hashable

        # pull out points from diagonal clustered point row
        for point_class_list in point_list:

            try:
                if child == point_class_list.flat_value:
                    child_points = point_class_list

            except:
                if child == [x.flat_value for x in point_class_list]:
                    child_points = point_class_list

        new_node = Node(cid, new_branch_id, father_node, line_num, child_points)

        if bid_father not in Graph.closed_keys:

            Graph.closed_keys.append(bid_father)

        if lame_parent == 1:
            if father_node not in Graph.lame_duck_parents:
                Graph.lame_duck_parents.append(father_node)

        # add the new orphan node
        Graph.cluster_dict[cid_father][new_branch_id] = [new_node]
        return new_node

    def mergeBranchToCluster(self, mcid, cluster_id, branch_id, close=1):

        """When you have a merge situation where each of the parent is from
        a differnt cluster you need to merge the two clusters"""

        node_list = Graph.cluster_dict[cluster_id][branch_id]
        # make all the cluster_id's the same
        for node in node_list:
            if type(node)==list:  #so if we hit a closed branch
                for closure_node in node:
                    closure_node.cluster_id = mcid
            else:
                node.cluster_id = mcid

        Graph.cluster_dict[mcid][branch_id] = node_list
        if close==1:
            if branch_id not in Graph.closed_keys:
                Graph.closed_keys.append(branch_id)  # then close the key

    def clean_lame_duck_parents(self, line_num):

        for lame_node in Graph.lame_duck_parents:
            if lame_node.line_count + 10 < line_num:
                Graph.lame_duck_parents.remove(lame_node)

    def calc_branch_length(self, branch_list):

        """Approximates how long a segment is that is represented by a node
        list. It does this by drawing a line through the centers of each node
        sequentially. Skipping the skip number between iterations. Then it adds
        up the line distances to approximate the overall length."""

        saved_centers = []
        increment = 0

        for node in branch_list:
            if increment % 4 == 0:  # get every 4th one
                try:  # get center coords

                    node_len = len(node.unpackChildren)
                    center_index = int(node_len/float(2))
                    center_coords = node.unpackChildren[center_index]
                except:
                    center_coords = node.unpackChildren

                saved_centers.append(center_coords)
            increment += 1

        if len(saved_centers) > 4:

            angle_difs = [calc_euclid_dist(x, saved_centers[i - 1])
                     for i, x in enumerate(saved_centers)][1:]
            length = sum(angle_difs)
        else:
            length = len(branch_list)

        return length  # branch length

    def get_coords_from_branch(self, branch_list):

        self.branch_list = branch_list
        singleton_list = []
        for node in self.branch_list:
            point_children = node.unpackChildren
            try:
                for coord in point_children:
                    singleton_list.append(coord)
            except:
                singleton_list.append(point_children)

        return singleton_list

    def get_node_from_flat(self, cid, flat_value):

        """Send in a flat matrix value and return the node that it is apart of"""

        branch_keys = grin.cluster_dict[cid].keys()

        for bkey in branch_keys:
            node_list = grin.cluster_dict[cid][bkey]
            for node in node_list:
                try:
                    if flat_value in node.flat_children:
                        return node
                except:
                    if flat_value == node.flat_children:
                        return node

    def calc_avg_branch_width(self, cid, bid):

        branch_width_sum = 0
        branch_list = self.get_branch_list(cid, bid, 1)
        branchlen = len(branch_list)
        for node in branch_list:
            branch_width_sum += node.width

        avg_node_width = int(branch_width_sum/float(branchlen))
        return avg_node_width

    def get_branch_height(self, cid, bid):

        branch_list = Graph.cluster_dict[cid][bid]
        start_line = branch_list[0].line_count
        for me in range(-1, -5, -1):
            try:
                end_line = branch_list[me].line_count
                break
            except:
                pass

        branch_height = abs(end_line - start_line) + 1
        return branch_height

    def get_branch_list(self, cid, bid, trunk=0):

        """Get the nodes from the branch id. We can toggle the trunk switch if
        we only want nodes that have a singleton child. If we don't toggle
        trunk then it returns all nodes in the branch"""

        if bid in self.cluster_dict[cid].keys():

            branch_list = self.cluster_dict[cid][bid]

            if branch_list:
                if trunk == 0:
                    return branch_list
                else:
                    return [branch for branch in branch_list if not isinstance(branch, list)]

    def get_branch_keys(self, cid):

        if cid in grin.cluster_dict.keys():
            return grin.cluster_dict[cid].keys()

    def closeParent(self, cid, bid, nodes):

        grin.add_node(cid, bid, nodes)

    def move_branch_to_new_layer(self, branch, layer=0):

        for node in branch:
            node.layer = layer
