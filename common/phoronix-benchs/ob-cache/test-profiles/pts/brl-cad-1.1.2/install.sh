#!/bin/sh

tar -xf brlcad-7.30.8.tar.bz2

 cp brlcad-7.30.8/src/other/libpng/scripts/pnglibconf.h.prebuilt brlcad-7.30.8/src/other/libpng/pnglibconf.h
mkdir brlcad-7.30.8/build
cd brlcad-7.30.8/build
cmake .. -DBRLCAD_ENABLE_STRICT=NO -DBRLCAD_BUNDLED_LIBS=ON -DBRLCAD_OPTIMIZED_BUILD=ON -DCMAKE_BUILD_TYPE=Release
make -j $NUM_CPU_CORES
echo $? > ~/install-exit-status
cd ~

echo "#!/bin/sh
cd brlcad-7.30.8/build
./bench/benchmark run -P\$NUM_CPU_CORES > \$LOG_FILE 2>&1
echo \$? > ~/test-exit-status" > brl-cad
chmod +x brl-cad


