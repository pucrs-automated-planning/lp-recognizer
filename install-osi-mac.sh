#!/usr/bin/env bash
# Ensure we are using the system's gcc/g++ rather than brew's
export PATH=/usr/bin:$PATH
pushd ..

# Uncomment the exports below if oyu want to run this outside of 'prepare-fd.sh'
# Check that this is where you have CPLEX (if you have it)
# export DOWNWARD_CPLEX_ROOT=/Applications/CPLEX_Studio129/cplex/
# You should probably change the line below to match where you want COIN64
# export DOWNWARD_COIN_ROOT=`pwd`/coin64
# You should probably change the line below to match where you want SOPLEX
# export DOWNWARD_SOPLEX_ROOT=`pwd`/soplex

# Install soplex
if [[ ! -d "$DOWNWARD_SOPLEX_ROOT" ]]; then
	# Install soplex
	echo "Installing SoPlex"
	wget -c  https://soplex.zib.de/download/release/soplex-3.1.1.tgz
	tar xvzf soplex-3.1.1.tgz
	pushd soplex-3.1.1
	cmake -DCMAKE_INSTALL_PREFIX="$DOWNWARD_SOPLEX_ROOT" .
	make -j8
	make install
	echo "Installed Soplex at $DOWNWARD_SOPLEX_ROOT"
	popd
fi


mkdir $DOWNWARD_COIN_ROOT
wget -c http://www.coin-or.org/download/source/Osi/Osi-0.107.9.tgz
tar xvzf Osi-0.107.9.tgz
pushd Osi-0.107.9

# Install osi
if [[ -d "$DOWNWARD_CPLEX_ROOT" ]]; then
	# Configure with CPLEX
	./configure CC="gcc"  CFLAGS="-m64 -arch x86_64 -pthread -Wno-long-long" \
	            CXX="g++" CXXFLAGS="-m64 -arch x86_64 -pthread -Wno-long-long" \
	            LDFLAGS="-L$DOWNWARD_CPLEX_ROOT/lib/x86-64_osx/static_pic -arch x86_64 -v \ 
						 -L$DOWNWARD_SOPLEX_ROOT/lib" \
	            --without-lapack --disable-shared --enable-static=yes \
	            --prefix="$DOWNWARD_COIN_ROOT" \
	            --disable-zlib --disable-bzlib \
 	            --with-soplex-lib="-lsoplex" \
 	            --with-cplex-incdir=$DOWNWARD_CPLEX_ROOT/include/ilcplex \
				--with-cplex-lib="-lcplex -lm -ldl"
else
	# Configure without CPLEX
	./configure CC="gcc"  CFLAGS="-m64 -pthread -Wno-long-long" \
	            CXX="g++" CXXFLAGS="-m64 -pthread -Wno-long-long" \
	            LDFLAGS="-L$DOWNWARD_SOPLEX_ROOT/lib" \
	            --without-lapack --enable-static=yes \
	            --prefix="$DOWNWARD_COIN_ROOT" \
	            --disable-bzlib \
	            --with-soplex-incdir=$DOWNWARD_SOPLEX_ROOT/include \
	            --with-soplex-lib="-lsoplex"
fi

make -j8
make install
popd
# rm -rf Osi-0.107.9
# rm Osi-0.107.9.tgz
echo "Installed OSI at $DOWNWARD_COIN_ROOT"

popd