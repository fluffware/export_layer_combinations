#!/usr/bin/python
import sys
import os
import re
import subprocess
import simplestyle
import inkex
import tempfile

def getLayers(element):
    groups = element.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.inkscape.org/namespaces/inkscape}groupmode='layer']")
    return groups

# show or hide a layer
def layerDisplay(layer, displayed):
    if "style" in layer.attrib:
        style = simplestyle.parseStyle(layer.attrib["style"])
    else:
        style = {}

    if displayed:
        style["display"]="inline"
    else:
        style["display"]="none"

    layer.attrib["style"] = simplestyle.formatStyle(style)

class LayerCombineExport(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        #super(LayerCombineExport, self).__init__()
        self.OptionParser.add_option('-p', '--prefix', action='store', type='string', dest='prefix', default="", help='Prefix prepended to the filename')
        self.OptionParser.add_option('-s', '--suffix', action='store', type='string', dest='suffix', default=".png", help='Suffix appended to the filename')
        self.OptionParser.add_option('-z', '--sizes', action='store', type='string', dest='sizes', default="", help='Comma separated list of sizes to export. Empty to use default')
        self.width = 0
        self.height = 0

    class LayerIter:
        def __init__(self):
            pass

        def __iter__(self):
            return self

        # Returns the label for next iteration
        def next(self):
            raise StopIteration()
        
        # Reset the iterator to it's start state
        def reset(self):
            pass

    class ExclusiveIter(LayerIter):
        def __init__(self, layers):
            LayerCombineExport.LayerIter.__init__(self)
            self.layers = layers
            self.index = 0

        def reset(self):
            self.index = 0
            
        def next(self):
            if self.index > 0:
                layerDisplay(self.layers[self.index - 1], False)

            if self.index >= len(self.layers):
                raise StopIteration()
            l = self.layers[self.index]
            label = l.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]
            label = re.match("(.*):iter\d+", label).group(1)
            layerDisplay(l, True)
            self.index += 1
            return label
            
    class SizeIter(LayerIter):
        def __init__(self, obj, sizes):
            LayerCombineExport.LayerIter.__init__(self)
            self.sizes = sizes
            self.obj = obj
            self.index = 0

        def reset(self):
            self.index = 0
            
        def next(self):
            if self.index >= len(self.sizes):
                raise StopIteration()
            s = self.sizes[self.index]
            self.obj.width = s[0]
            self.obj.height = s[1]
            label = "_%dx%d" % (s[0], s[1])
            self.index += 1
            return label
            

    def iterate_layers(self, levels, level, prefix):
        if level < len(levels):
            i = levels[level]
            i.reset()
            for label in i:
                self.iterate_layers(levels, level + 1, prefix + label);
        else:
            (ref, tmp_svg) = tempfile.mkstemp('.svg')
            self.document.write( tmp_svg )
            cmd =["inkscape"]
            if self.width > 0 and self.height > 0:
                cmd += ["--export-width=%d" % (self.width),"--export-height=%d" % (self.height)]
            cmd += ["--export-area-page",("--export-png="+prefix+self.options.suffix), tmp_svg]
            status = subprocess.call(cmd, stdout=sys.stderr, stderr=sys.stderr)	
            if status != 0:
                inkex.erromsg(_("Inkscape returned an error when saving PNG:"))
            #inkex.debug(cmd)
            os.close(ref)
            os.remove(tmp_svg)

    def effect(self):
        iterations = {}
        always = []
        levels = []

        iterpat = re.compile(".*:iter(\d+)")
        alwayspat = re.compile(".*:always")
        layers = getLayers(self.document)
        for l in layers:
            label = l.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]
            #inkex.debug(label)
            mo = iterpat.match(label)
            if mo:
                n = int(mo.group(1))
                if n in iterations:
                    iterations[n].append(l)
                else:
                    iterations[n] = [l]
                layerDisplay(l, False)

            else:
                if alwayspat.match(label):
                    layerDisplay(l, True)
                else:
                    # hide unknown layers
                    layerDisplay(l, False)
                    
                    
        # sort iteration levels and put them in an array
        for i in sorted(iterations):
            levels.append(LayerCombineExport.ExclusiveIter(iterations[i]))

        if len(self.options.sizes) > 0:
            sizes = []
            dims = self.options.sizes.split(",")
            for d in dims:
                m = re.match("(\d+)[xX](\d+)", d)
                if m:
                    sizes.append([int(m.group(1)), int(m.group(2))])
            if sizes:
                levels.append(LayerCombineExport.SizeIter(self, sizes))

        #inkex.debug(levels)
        self.iterate_layers(levels, 0, self.options.prefix)
        

export = LayerCombineExport()
export.affect(sys.argv[1:], False)

