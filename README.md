export_layer_combinations
=========================

Inkscape extension that saves multiple PNG files containing different combinations of layers. 
To install just copy the files to the extension directory.

The scripts needs special layer names to function.
The names consists of two parts separated by a colon.
The part before the colon is used when generating the filenames for the exported files.
The second part decides how the layer is combined with others when exported.

<name>:allways	  The layer is part of all exported files. <name> is ignored.

<name>:iter<n>	  <n> tells which group the layer belongs to. Only one layer
		  from each group is included in each exported file. Names
		  are added to the filename in ascending order of <n>.
		  Different <n> does not need to be consecutive.

Layers with names that doesn't match any of the patterns are not exported.

The script has three parameters:

Prefix	   The first part of the filename including the full path. Layer names
	   are added to this part.

Suffix	   Appended to the end of the file name.

Sizes	   A comma separated list of sizes for the exported bitmaps in the
	   format <width>x<height>

Example:
Suppose the Inkscape document has the following layers:

_1:iter4
_2:iter4
_A:iter1
_B:iter1
Background:always

and the parameters for the script is:

Prefix: /tmp/foo
Suffix: .png
Sizes: 16x20,32x40

Running the script will produce 8 files:

/tmp/foo_A_1_16x20
/tmp/foo_A_1_32x40
/tmp/foo_A_2_16x20
/tmp/foo_A_2_32x40
/tmp/foo_B_1_16x20
/tmp/foo_B_1_32x40
/tmp/foo_B_2_16x20
/tmp/foo_B_2_32x40

Each will contain the layers listed in the filename in addition to the 
background layer.
