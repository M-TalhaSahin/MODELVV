import xml.etree.ElementTree as ET


class Template:
    def __init__(self, tmpName, tmpNodes, tmpEdges):
        self.name = tmpName
        self.nodeList = tmpNodes
        self.edgeList = tmpEdges


class Edge:
    def __init__(self, Src, Tgt, labels, nailList):
        self.src = Src
        self.tgt = Tgt
        self.nails = nailList
        self.labelList = labels


class Node:
    def __init__(self, Id, X, Y, Name, nx, ny):
        self.id = Id
        self.x = X
        self.y = Y
        self.name = Name
        self.namex = nx
        self.namey = ny


def getNodeEdgeList(xmlFileName):
    """
    tree = ET.parse(xmlFileName)  # 'nodes_s.xml'
    root = tree.getroot()
    """
    dimension = 3
    root = ET.fromstring(xmlFileName)

    tempList = []

    for actor in root.findall('template'):
        tempNode = []
        tempEdge = []
        for child in actor.findall('location'):
            try:
                hold_node = Node(int(child.attrib['id'][2:]), float(child.attrib['x']) * dimension,
                                 (float(child.attrib['y']) - 9) * dimension, child[0].text,
                                 (float(child[0].attrib['x']) - float(child.attrib['x'])) * dimension,
                                 (float(child[0].attrib['y']) - float(child.attrib['y']) + 9) * dimension)
            except KeyError:
                hold_node = Node(int(child.attrib['id'][2:]), float(child.attrib['x']) * dimension,
                                 (float(child.attrib['y']) - 9) * dimension, '', -1, -1)
            tempNode.append(hold_node)

        for child in actor.findall('transition'):
            labels = []
            for lbl in child.findall('label'):
                labels.append({'lblKind': lbl.attrib['kind'], 'lblText': lbl.text, 'coordX': int(lbl.attrib['x']) * dimension, 'coordY': int(lbl.attrib['y']) * dimension})

            nailList = []
            for nails in child.findall('nail'):
                nailList.append([float(float(nails.attrib['x']) + 9) * dimension, float(nails.attrib['y']) * dimension])

            hold_edge = Edge(int(child[0].attrib['ref'][2:]), int(child[1].attrib['ref'][2:]), labels, nailList)

            tempEdge.append(hold_edge)

        tmp = Template(actor[0].text, tempNode, tempEdge)
        tempList.append(tmp)

    return tempList

