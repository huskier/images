from __future__ import print_function

import sys
sys.path.append('/usr/lib/freecad/bin')

import cadquery as cq

from cadquery import *

import FreeCAD

import Part as FreeCADPart

from OCC.BRep import BRep_Tool

from OCC.TopAbs import (TopAbs_VERTEX, TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE,
                        TopAbs_SHELL, TopAbs_SOLID, TopAbs_COMPOUND,
                        TopAbs_COMPSOLID)
                        
from OCC.TopExp import TopExp_Explorer, topexp_MapShapesAndAncestors
from OCC.TopTools import (TopTools_ListOfShape,
                          TopTools_ListIteratorOfListOfShape,
                          TopTools_IndexedDataMapOfShapeListOfShape)
from OCC.TopoDS import (topods, TopoDS_Wire, TopoDS_Vertex, TopoDS_Edge,
                        TopoDS_Face, TopoDS_Shell, TopoDS_Solid,
                        TopoDS_Compound, TopoDS_CompSolid, topods_Edge,
                        topods_Vertex, topods_Wire, TopoDS_Iterator)                        

from OCC.STEPControl import STEPControl_Reader
from OCC.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Display.SimpleGui import init_display

from OCCUtils.Construct import (make_closed_polygon, make_n_sided,
                                make_vertex, make_face)
from OCCUtils.Topology import WireExplorer, Topo, dumpTopology

from OCC.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge,
                                BRepBuilderAPI_MakeFace,
                                BRepBuilderAPI_MakeWire)
from OCC.gp import gp_Pnt, gp_Vec
from OCC.BRepPrimAPI import BRepPrimAPI_MakePrism                                

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

lstWires = []

# CQ2PythonOCC()......
# PythonOCC2CQ()......


def mydumpTopology(shape, level=0):
    """
     Print the details of an object from the top down
    """
    brt = BRep_Tool()
    s = shape.ShapeType()
    if s == TopAbs_VERTEX:
        pnt = brt.Pnt(topods_Vertex(shape))
        print(".." * level  + "<Vertex %i: %s %s %s>" % (hash(shape), pnt.X(), pnt.Y(), pnt.Z()))
    else:
        print(".." * level, end="")
        if s == TopAbs_WIRE:
            lstWires.append(shape)
            print("shape type is TopAbs_WIRE...")
    it = TopoDS_Iterator(shape)
    while it.More():
        shp = it.Value()
        it.Next()
        mydumpTopology(shp, level + 1)

step_reader = STEPControl_Reader()

status = step_reader.ReadFile('/home/huskier/Public/cad/SectionBar_ZDir.step')


if status == IFSelect_RetDone:  # check status
    failsonly = False
    step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
    step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)

    ok = step_reader.TransferRoot(1)
    _nbs = step_reader.NbShapes()
    aResShape = step_reader.Shape(1)
else:
    print("Error: can't read file.")
    sys.exit(0)


mydumpTopology(aResShape)


print(len(lstWires))

face = BRepBuilderAPI_MakeFace(topods_Wire(lstWires[-1]))

starting_point = gp_Pnt(0., 0., 0.)
end_point = gp_Pnt(0., 0., 100.)
vec = gp_Vec(starting_point, end_point)

prism = BRepPrimAPI_MakePrism(face.Shape(), vec).Shape()

freecadObj = FreeCADPart.Wire(FreeCADPart.__fromPythonOCC__(lstWires[-1]))

print(str(type(freecadObj)))

cqObj = cq.CQ(freecadObj)

cqObj = Wire(cqObj)

print(str(type(cqObj)))

wkplane = cq.Workplane("XY").addWires(cqObj).extrude(20)
#print(str(type(wkplane)))
#print(wkplane.wires().size())

display.DisplayShape(prism, update=False) 

start_display()


