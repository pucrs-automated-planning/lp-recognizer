#!/usr/bin/python
import sys, os

def merge_tables(tex1, tex2):
	# Get number of rows
	astart = tex1.find("\\begin{tabular}{") + 16
	align = tex1[astart:-1]
	aend = align.find("}")
	align = align[0:aend]
	align = align.replace("|", "")
	nrows = len(align)
	# Get tex2 content
	start = tex2.find("% tablestart") + 13
	end = tex2.find("% tableend")
	title = "\\multicolumn{" + str(nrows) + "}{c}{Sub-Optimal}" 
	header = "\n\\\\\\midrule\n" + title + "\\\\\\toprule\n" 
	# Merge
	return tex1.replace("% tableend", header + tex2[start:end] + "% tableend")

if __name__ == '__main__' :
	with open(sys.argv[1] + ".tex", 'r') as f:
		tex1 = f.read()
	with open(sys.argv[2] + ".tex", 'r') as f:
		tex2 = f.read()
	with open(sys.argv[1] + "-merge.tex", 'w') as f:
		f.write(merge_tables(tex1, tex2))
	os.system("pdflatex " + sys.argv[1] + "-merge.tex")