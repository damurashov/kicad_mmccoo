# Copyright [2017] [Miles McCoo]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# this script is a basic svg generator for pcbnew.
# the point of the script is more as a teaching tool
# there are a number of ways in which is is deficient.


import pcbnew

# if you get the error: importError: No module named svgwrite
#    you need to do "pip install svgwrite" in an xterm



padshapes = {
    pcbnew.PAD_SHAPE_CIRCLE:  "PAD_SHAPE_CIRCLE",
    pcbnew.PAD_SHAPE_OVAL:    "PAD_SHAPE_OVAL",
    pcbnew.PAD_SHAPE_RECT:    "PAD_SHAPE_RECT",
    pcbnew.PAD_SHAPE_TRAPEZOID: "PAD_SHAPE_TRAPEZOID"    
}
# new in the most recent kicad code
if hasattr(pcbnew, 'PAD_SHAPE_ROUNDRECT'):
    padshapes[pcbnew.PAD_SHAPE_ROUNDRECT] = "PAD_SHAPE_ROUNDRECT",


    
board = pcbnew.GetBoard()

boardbbox = board.ComputeBoundingBox()
boardxl = boardbbox.GetX()
boardyl = boardbbox.GetY()
boardwidth = boardbbox.GetWidth()
boardheight = boardbbox.GetHeight()

# coordinate space of kicad_pcb is in mm. At the beginning of
# https://en.wikibooks.org/wiki/Kicad/file_formats#Board_File_Format
# "All physical units are in mils (1/1000th inch) unless otherwise noted."
# then later in historical notes, it says,
# As of 2013, the PCBnew application creates ".kicad_pcb" files that begin with
# "(kicad_pcb (version 3)". All distances are in millimeters. 

# the internal coorinate space of pcbnew is 10E-6 mm. (a millionth of a mm)
# the coordinate 121550000 corresponds to 121.550000 

SCALE = 1000000.0


import sys, os
import svgwrite

print("working in the dir " + os.getcwd())
name = "output.svg"
# A4 is approximately 21x29
dwg = svgwrite.Drawing(name, size=('21cm', '29cm'), profile='full', debug=True)

dwg.viewbox(width=boardwidth, height=boardheight, minx=boardxl, miny=boardyl)
background = dwg.add(dwg.g(id='bg', stroke='white'))
background.add(dwg.rect(insert=(boardxl, boardyl), size=(boardwidth, boardheight), fill='white'))



svglayers = {}
colors = board.Colors()
for layerid in range(pcbnew.PCB_LAYER_ID_COUNT):
    c4 = colors.GetLayerColor(layerid);
    colorrgb = "rgb({:d}, {:d}, {:d})".format(int(round(c4.r*255)),
                                              int(round(c4.g*255)),
                                              int(round(c4.b*255)));
    layer = dwg.add(dwg.g(id='layer_'+str(layerid), stroke=colorrgb, stroke_linecap="round"))
    svglayers[layerid] = layer

alltracks = board.GetTracks() 
for track in alltracks:
    # print("{}->{}".format(track.GetStart(), track.GetEnd()))
    # print("{},{}->{},{} width {} layer {}".format(track.GetStart().x/SCALE, track.GetStart().y/SCALE,
    #                                               track.GetEnd().x/SCALE,   track.GetEnd().y/SCALE,
    #                                               track.GetWidth()/SCALE,
    #                                               track.GetLayer())          
    # )
    svglayers[track.GetLayer()].add(dwg.line(start=(track.GetStart().x,
                                                    track.GetStart().y),
                                             end=(track.GetEnd().x,
                                                  track.GetEnd().y),
                                             stroke_width=track.GetWidth()
    ))


svgpads = dwg.add(dwg.g(id='pads', stroke='red',fill='orange'))
allpads = board.GetPads()

for pad in allpads:
    mod = pad.GetParent()
    name = pad.GetPadName()
    if (0):
        print("pad {}({}) on {}({}) at {},{} shape {} size {},{}"
              .format(name,
                      pad.GetNet().GetNetname(),
                      mod.GetReference(),
                      mod.GetValue(),
                      pad.GetPosition().x, pad.GetPosition().y,
                      padshapes[pad.GetShape()],
                      pad.GetSize().x, pad.GetSize().y
              ))
    if (pad.GetShape() == pcbnew.PAD_SHAPE_RECT):
        if ((pad.GetOrientationDegrees()==270) | (pad.GetOrientationDegrees()==90)):
            svgpads.add(dwg.rect(insert=(pad.GetPosition().x-pad.GetSize().x/2,
                                         pad.GetPosition().y-pad.GetSize().y/2),
                                 size=(pad.GetSize().y, pad.GetSize().x)))
        else:
            svgpads.add(dwg.rect(insert=(pad.GetPosition().x-pad.GetSize().x/2,
                                         pad.GetPosition().y-pad.GetSize().y/2),
                                 size=(pad.GetSize().x, pad.GetSize().y)))
    elif (pad.GetShape() == pcbnew.PAD_SHAPE_CIRCLE):
        svgpads.add(dwg.circle(center=(pad.GetPosition().x, pad.GetPosition().y),
                               r=pad.GetSize().x))
    elif (pad.GetShape() == pcbnew.PAD_SHAPE_OVAL):
        svgpads.add(dwg.ellipse(center=(pad.GetPosition().x, pad.GetPosition().y),
                                r=(pad.GetSize().x/2, pad.GetSize().y/2)))
    else:
        print("unknown pad shape {}({})".format(pad.GetShape(), padshapes[pad.GetShape()]))


    
dwg.save()
 

print("done")
