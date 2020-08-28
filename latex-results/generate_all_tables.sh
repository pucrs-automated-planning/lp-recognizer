#!/usr/bin/env bash

./generate_tables.py -t previous-template.tex -f previous.tex
./generate_tables.py -t previous-template.tex -f previous-noisy.tex
./generate_tables.py -t previous-template.tex -f previous-old-noisy.tex
./generate_tables.py -t constraints-single-template.tex -f constraints-single.tex
./generate_tables.py -t constraints-single-template.tex -f constraints-single-noisy.tex
./generate_tables.py -t constraints-pairs-template.tex -f constraints-pairs.tex
./generate_tables.py -t constraints-pairs-template.tex -f constraints-pairs-noisy.tex
./generate_tables.py -t filters-template.tex -f filters-noisy.tex
./generate_tables.py -t filters-template.tex -f filters-old-noisy.tex
#./generate_tables.py -t variations-template.tex -f variations.tex
#./generate_tables.py -t variations-template.tex -f variations-noisy.tex
#./generate_tables.py -t variations-template.tex -f variations-old-noisy.tex