#!/usr/bin/env python
# coding: utf8

# (c) 2014 Dominic Springer
# File licensed under GNU GPL (see HARP_License.txt)

import os
import sys
import numpy as np
import re
import pickle
import gzip
import math as m
import time

import types

#from GraphViz import *

#==========================================
def draw_Dict(Dict, NameRootNode, FN_Base):
#==========================================
    import pygraphviz as pgv

    Ranksep = '0.2'

    G = pgv.AGraph(directed=True, ranksep=Ranksep, rankdir="TB", dpi=300)
    G.graph_attr['overlap']='false'
    #G.graph_attr['bgcolor']='gray'
    G.node_attr['shape']='box'

    
    Depth = -1
    NameRootNode = Dict["Name"] + " (dict)" if "Name" in Dict else NameRootNode
    G.add_node(NameRootNode, color='red', fontcolor="red", penwidth=3)
    drawDictContents(NameRootNode, Dict, Depth, G)
    
    G.layout() # default to neato
    G.layout(prog='dot') # use dot
    
    #G.write('raw.dot')
    G.draw(FN_Base +  ".png")
    G.write(FN_Base + ".dot")
    print("draw_Dict: wrote %s.[png/dot]" +  FN_Base)
    
#==========================================
def addNode(ParentName, ChildName, Color, G):
#==========================================
    G.add_node(ChildName, color=Color, fontcolor=Color, penwidth=3)
    G.add_edge(ParentName, ChildName, shape='box', penwidth=3)
    
#==========================================
def drawDictContents(ParentName, Dict, Depth, G):
#==========================================
    Depth = Depth + 1
    
    ListColor = "blue"
    DictColor = "red"
    NumpyColor = "darkgreen"
    
    
    
    #-------------------------------------
    # SORTING
    #-------------------------------------
    OrigKeys = Dict.keys();
    Keys = []
    
    if Depth == 2:
        for Entry in OrigKeys:
            if type(Dict[Entry]) is types.ListType:
                Keys.append(Entry)
    

    
    for Entry in OrigKeys:
        t=type(Dict[Entry])
        if t is not types.ListType and t is not types.DictType and t is not np.ndarray:
            Keys.append(Entry)
            
    for Entry in OrigKeys:
        if type(Dict[Entry]) is types.DictType:
            Keys.append(Entry)
            
    for Entry in OrigKeys:
        if type(Dict[Entry]) is np.ndarray:
            Keys.append(Entry)
            
#     for Entry in OrigKeys:
#         if type(Dict[Entry]) is types.ListType:
#             Keys.append(Entry)
            
    if Depth != 2:
        for Entry in OrigKeys:
            if type(Dict[Entry]) is types.ListType:
                Keys.append(Entry)

            
    #-------------------------------------
    # DRAWING
    #-------------------------------------
    for Entry in Keys:
        
        EntryType = type(Dict[Entry])  #DIFF
            
        if EntryType is types.ListType:
            #draw: list box + recursion
            print "Entry %s is a list (%d entries)"  % (Entry, len(Dict[Entry]))
            NodeName = Entry + "[ ]" + " (list)" + ' '*Depth
            addNode(ParentName, NodeName, ListColor, G)
            if 0: #"Ref" in Entry:
                continue
            else:
                drawListContents(NodeName, Dict[Entry], Depth, G)
        elif EntryType is types.DictType:
            #draw: dict box + recursion
            print "Entry %s is a dict"  % Entry
            Name = Entry["Name"] if "Name" in Entry else ""
            NodeName = Entry + " (dict)" + ' '*Depth
            addNode(ParentName, NodeName, DictColor, G)
            drawDictContents(NodeName, Dict[Entry], Depth, G)     
        elif  EntryType is np.ndarray: 
            #draw: ndarray
             print "Entry %s is ndarray" % Entry
#             NodeName = Entry + " (ndarray)" + ' '*Depth
#             addNode(ParentName, NodeName, NumpyColor, G)
        elif Entry == "Name":
            pass
        else:
            #draw: plain attribute
            print "Entry %s is an attribute"  % Entry
            NodeName = Entry + " "*Depth
            addNode(ParentName, NodeName, "black", G)
            #G.add_edge(ParentName, NodeName, shape='box')

#==========================================
def drawListContents(ParentName, List, Depth, G):
#==========================================
    Depth = Depth + 1

    ListColor = "blue"
    DictColor = "red"
    NumpyColor = "darkgreen"
    

    for Entry in List:
        
        EntryType = type(Entry) #DIFF
        
        if EntryType is types.ListType:
            #draw: list box + recursion
            print "Entry is a list (%d entries)"  % (len(Entry)) #DIFF
            NodeName = Entry + "[ ]" + " (list)" + ' '*Depth
            addNode(ParentName, NodeName, ListColor, G)
            drawListContents(NodeName, Entry, Depth, G)  #DIFF
        elif EntryType is types.DictType:
            #draw: dict box + recursion
            print "Entry is a dict"  
            Name = Entry["Name"] if "Name" in Entry else ""
            NodeName = Name + " (dict)" + ' '*Depth
            addNode(ParentName, NodeName, DictColor, G)
            if "POC" in Name:
                continue
            else:
                drawDictContents(NodeName, Entry, Depth, G)  #DIFF
        elif EntryType is np.ndarray:
            #draw: ndarray
             print "Entry is ndarray" 
#             NodeName = "ndarray" + " "*Depth  #DIFF
#             addNode(ParentName, NodeName, NumpyColor, G)  
        else:  #anything else: do NOT draw
            pass
