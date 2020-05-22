#!/usr/bin/env bash
pushd ..
mkdir $DOWNWARD_COIN_ROOT
wget -c http://www.coin-or.org/download/source/Osi/Osi-0.107.9.tgz
tar xvzf Osi-0.107.9.tgz
cd Osi-0.107.9
# If CPLEX is installed
if [[ -d "$DOWNWARD_CPLEX_ROOT" ]]; then
	./configure CC="gcc"  CFLAGS="-m64 -pthread -Wno-long-long" \
	            CXX="g++" CXXFLAGS="-m64 -pthread -Wno-long-long" \
	            LDFLAGS="-L$DOWNWARD_CPLEX_ROOT/lib/x86-64_linux/static_pic" \
	            --without-lapack --enable-static=yes \
	            --prefix="$DOWNWARD_COIN_ROOT" \
	            --disable-zlib --disable-bzlib \
	            --with-cplex-incdir=$DOWNWARD_CPLEX_ROOT/include/ilcplex --with-cplex-lib="-lcplex -lm -ldl"
else
	if [[ ! -d "$DOWNWARD_SOPLEX_ROOT" ]]; then
		pushd ..
		export DOWNWARD_SOPLEX_ROOT=`pwd`/soplex
		# Install soplex
		wget -c  https://soplex.zib.de/download/release/soplex-3.1.1.tgz
		tar xvzf soplex-3.1.1.tgz
		cd soplex-3.1.1
		cmake -DCMAKE_INSTALL_PREFIX="$DOWNWARD_SOPLEX_ROOT" .
		make
		make install
		cd ..
		popd
	fi
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
cd ..
popd