#!/usr/bin/env bash

##
## Generate .pdf tables for all methods.
##

## Uses:
# Generate full individual tables for each data set type:
# ./generate_all_tables.sh full [-fast]
# Generate full tables for optimal merged with summarized table for sub-optimal type:
# ./generate_all_tables.sh merge [-fast]
##

# Generate indivisual tables for optimal data sets.
./generate_tables.py lm -rows -comp $2
./generate_tables.py lmf2-old-noisy -rows -comp $2
./generate_tables.py del -rows -comp $2
./generate_tables.py delf2-old-noisy -rows -comp $2
./generate_tables.py flow -rows -comp $2
./generate_tables.py flowf2-old-noisy -rows -comp $2
#./generate_tables.py basic
#./generate_tables.py basicf2-old-noisy
#./generate_tables.py basic-sub
#./generate_tables.py basicf2-sub-old-noisy

# Genarate tables for sub-optimal data sets.
if [[ "$1" == "merge" ]]; then
	./generate_tables.py lm-sub -rows -comp -obs $2
	./generate_tables.py lmf2-sub-old-noisy -rows -comp -obs $2
	./generate_tables.py del-sub -rows -comp -obs $2
	./generate_tables.py delf2-sub-old-noisy -rows -comp -obs $2
	./generate_tables.py flow-sub -rows -comp -obs $2
	./generate_tables.py flowf2-sub-old-noisy -rows -comp -obs $2
	./merge_tables.py lm lm-sub -vertical
	./merge_tables.py lmf2-old-noisy lmf2-sub-old-noisy -vertical
	./merge_tables.py del del-sub -vertical
	./merge_tables.py delf2-old-noisy delf2-sub-old-noisy -vertical
	./merge_tables.py flow flow-sub -vertical
	./merge_tables.py flowf2-old-noisy flowf2-sub-old-noisy -vertical
else
	./generate_tables.py lm-sub -rows -comp $2
	./generate_tables.py lmf2-sub-old-noisy -rows -comp $2
	./generate_tables.py del-sub -rows -comp $2
	./generate_tables.py delf2-sub-old-noisy -rows -comp $2
	./generate_tables.py flow-sub -rows -comp $2
	./generate_tables.py flowf2-sub-old-noisy -rows -comp $2
fi

rm *.txt *.aux