#!/usr/bin/env bash

##
## Generate .pdf tables for all methods.
##

## Uses:
# Generate full individual tables for each data set type:
# ./generate_all_tables.sh full [-fast]
# Generate full tables for optimal merged with summarized table for sub-optimal type:
# ./generate_all_tables.sh merge [-fast]
# Generate summarized tables:
# ./generate_all_tables.sh avg [-fast]
##

if [[ "$1" == "v2" ]]; then
	./generate_tables.py lmc -rows -obs -v2
	./generate_tables.py lmc-sub -rows -obs -v2
	./generate_tables.py lmcf2-old-noisy -rows -obs -v2
	./generate_tables.py lmcf2-sub-old-noisy -rows -v2
	./generate_tables.py delr -rows -obs -v2
	./generate_tables.py delr-sub -rows -obs -v2
	./generate_tables.py delrf2-old-noisy -rows -v2
	./generate_tables.py delrf2-sub-old-noisy -rows -v2
elif [[ "$1" == "avg" ]]; then
	./generate_tables.py lmc -rows -obs $2
	./generate_tables.py lmc-sub -rows -obs $2
	./generate_tables.py lmcf2-old-noisy -rows -obs $2
	./generate_tables.py lmcf2-sub-old-noisy -rows -obs $2
	./generate_tables.py delr -rows -obs $2
	./generate_tables.py delr-sub -rows -obs $2
	./generate_tables.py delrf2-old-noisy -rows -obs $2
	./generate_tables.py delrf2-sub-old-noisy -rows -obs $2
	./generate_tables.py flow -rows -obs $2
	./generate_tables.py flow-sub -rows -obs $2
	./generate_tables.py flowf2-old-noisy -rows -obs $2
	./generate_tables.py flowf2-sub-old-noisy -rows -obs $2
	./generate_tables.py general -time -obs $2
	./generate_tables.py general-sub -time -obs $2
	./generate_tables.py general-old-noisy -time -obs $2
	./generate_tables.py general-sub-old-noisy -time -obs $2
else
	# Generate indivisual tables for optimal data sets.
	./generate_tables.py lmc -rows $2
	#./generate_tables.py lmcd -rows $2
	./generate_tables.py lmcf2-old-noisy -rows $2
	./generate_tables.py delr -rows $2
	./generate_tables.py delrf2-old-noisy -rows $2
	./generate_tables.py flow -rows $2
	./generate_tables.py flowf2-old-noisy -rows $2
	#./generate_tables.py basic
	#./generate_tables.py basicf2-old-noisy
	#./generate_tables.py basic-sub
	#./generate_tables.py basicf2-sub-old-noisy
	./generate_tables.py general -time $2
	./generate_tables.py general-old-noisy -time $2

	# Genarate tables for sub-optimal data sets.
	if [[ "$1" == "merge" ]]; then
		./generate_tables.py lmc-sub -rows -obs $2
		#./generate_tables.py lmcd-sub -rows -obs $2
		./generate_tables.py lmcf2-sub-old-noisy -rows -obs $2
		./generate_tables.py delr-sub -rows -obs $2
		./generate_tables.py delrf2-sub-old-noisy -rows -obs $2
		./generate_tables.py flow-sub -rows -obs $2
		./generate_tables.py flowf2-sub-old-noisy -rows -obs $2
		./merge_tables.py lmc lmc-sub -vertical
		./merge_tables.py lmcf2-old-noisy lmcf2-sub-old-noisy -vertical
		./merge_tables.py delr delr-sub -vertical
		./merge_tables.py delrf2-old-noisy delrf2-sub-old-noisy -vertical
		./merge_tables.py flow flow-sub -vertical
		./merge_tables.py flowf2-old-noisy flowf2-sub-old-noisy -vertical
		./generate_tables.py general-sub -time -obs $2
		./generate_tables.py general-sub-old-noisy -time -obs $2
		./merge_tables.py general general-sub -vertical
		./merge_tables.py general-old-noisy general-sub-old-noisy -vertical
	else
		./generate_tables.py lmc-sub -rows $2
		#./generate_tables.py lmcd-sub -rows $2
		./generate_tables.py lmcf2-sub-old-noisy -rows $2
		./generate_tables.py delr-sub -rows $2
		./generate_tables.py delrf2-sub-old-noisy -rows $2
		./generate_tables.py flow-sub -rows $2
		./generate_tables.py flowf2-sub-old-noisy -rows $2
		./generate_tables.py general-sub -time $2
		./generate_tables.py general-sub-old-noisy -time $2
	fi
fi

rm ./*.txt ./*.aux