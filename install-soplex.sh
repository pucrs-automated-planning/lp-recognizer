#!/usr/bin/env bash

pushd ..
	# Set soplex path
	if [[ -z "$soplex_DIR" ]]; then
		export soplex_DIR=/opt/soplex-6.0.4x
		echo "export soplex_DIR=\"${soplex_DIR}\"" >> ~/.profile
	fi
	# Check for soplex in path
	if [[ ! -d "$soplex_DIR" ]]; then
		git clone https://github.com/scipopt/soplex.git soplexrepo
		export CXXFLAGS="$CXXFLAGS -Wno-use-after-free" # Ignore compiler warnings about use-after-free
		cmake -S soplexrepo -B build
		cmake --build build
		sudo cmake --install build --prefix $soplex_DIR
		rm -rf soplexrepo build
		if [[ -z "$soplex_DIR" ]]; then 
			echo "Failed to install Soplex. Install CPLEX manually.";
		else
			echo "export lpr_solver=soplex" >> ~/.profile;
		fi
	else
		echo "Soplex Present"
	fi
popd