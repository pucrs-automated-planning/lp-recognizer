#!/usr/bin/env bash
export DOWNWARD_CPLEX_ROOT=/opt/ibm/ILOG/CPLEX_Studio129/cplex
# You should probably change the line below to match where you want COIN64
pushd ..
export DOWNWARD_COIN_ROOT=`pwd`/coin64 
mkdir $DOWNWARD_COIN_ROOT
wget -c http://www.coin-or.org/download/source/Osi/Osi-0.107.9.tgz
tar xvzf Osi-0.107.9.tgz
cd Osi-0.107.9
./configure CC="gcc"  CFLAGS="-m64 -pthread -Wno-long-long" \
            CXX="g++" CXXFLAGS="-m64 -pthread -Wno-long-long" \
            LDFLAGS="-L$DOWNWARD_CPLEX_ROOT/lib/x86-64_linux/static_pic" \
            --without-lapack --enable-static=yes \
            --prefix="$DOWNWARD_COIN_ROOT" \
            --disable-zlib --disable-bzlib \
            --with-cplex-incdir=$DOWNWARD_CPLEX_ROOT/include/ilcplex --with-cplex-lib="-lcplex -lm -ldl"
make
make install
cd ..
# rm -rf Osi-0.107.9
# rm Osi-0.107.9.tgz
popd