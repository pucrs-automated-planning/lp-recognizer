#!/usr/bin/env bash
pushd ..

# Uncomment the exports below if oyu want to run this outside of 'prepare-fd.sh'
# Check that this is where you have CPLEX (if you have it)
# export DOWNWARD_CPLEX_ROOT=/opt/ibm/ILOG/CPLEX_Studio129/cplex
# You should probably change the line below to match where you want COIN64
# export DOWNWARD_COIN_ROOT=`pwd`/coin64
# You should probably change the line below to match where you want SOPLEX
# export DOWNWARD_SOPLEX_ROOT=`pwd`/soplex

# Install soplex
if [[ ! -d "$DOWNWARD_SOPLEX_ROOT" ]]; then
	# Install soplex
	wget -c  https://soplex.zib.de/download/release/soplex-3.1.1.tgz
	tar xvzf soplex-3.1.1.tgz
	pushd soplex-3.1.1
	cmake -DCMAKE_INSTALL_PREFIX="$DOWNWARD_SOPLEX_ROOT" .
	make
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
	./configure CC="gcc"  CFLAGS="-pthread -Wno-long-long" \
	            CXX="g++" CXXFLAGS="-pthread -Wno-long-long" \
	            LDFLAGS="-L$DOWNWARD_CPLEX_ROOT/lib/x86-64_linux/static_pic \
	                     -L$DOWNWARD_SOPLEX_ROOT/lib" \
	            --without-lapack --enable-static=no \
	            --prefix="$DOWNWARD_COIN_ROOT" \
	            --disable-bzlib \
	            --with-soplex-incdir=$DOWNWARD_SOPLEX_ROOT/include \
	            --with-soplex-lib="-lsoplex" \
	            --with-cplex-incdir=$DOWNWARD_CPLEX_ROOT/include/ilcplex \
	            --with-cplex-lib="-lcplex -lm -ldl" # -ldl is only needed for CPLEX >= 12.8
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
make
make install
popd
echo "Installed OSI at $DOWNWARD_COIN_ROOT"

popd