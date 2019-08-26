#!/usr/bin/env bash
# Ensure we are using the system's gcc/g++ rather than brew's
export PATH=/usr/bin:$PATH
pushd ..
export DOWNWARD_CPLEX_ROOT=/Applications/CPLEX_Studio129/cplex/
# You should probably change the line below to match where you want COIN64
export DOWNWARD_COIN_ROOT=`pwd`/coin64
mkdir $DOWNWARD_COIN_ROOT
wget -c http://www.coin-or.org/download/source/Osi/Osi-0.107.9.tgz
tar xvzf Osi-0.107.9.tgz
cd Osi-0.107.9

./configure CC="gcc"  CFLAGS="-m64 -arch x86_64 -pthread -Wno-long-long" \
            CXX="g++" CXXFLAGS="-m64 -arch x86_64 -pthread -Wno-long-long" \
            LDFLAGS="-L$DOWNWARD_CPLEX_ROOT/lib/x86-64_osx/static_pic -arch x86_64 -v" \
            --without-lapack --disable-shared --enable-static=yes \
            --prefix="$DOWNWARD_COIN_ROOT" \
            --disable-zlib --disable-bzlib \
            --with-cplex-incdir=$DOWNWARD_CPLEX_ROOT/include/ilcplex --with-cplex-lib="-lcplex -lm -ldl"

make -j8
make install
cd ..
# rm -rf Osi-0.107.9
# rm Osi-0.107.9.tgz
popd