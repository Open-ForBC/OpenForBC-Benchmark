#!/bin/sh

tar -xf cpuminer-opt-3.15.5.tar.gz
cd cpuminer-opt-3.15.5
./autogen.sh 
CFLAGS="-O3 -march=native $CFLAGS" ./configure --without-curl

if [ $OS_TYPE = "BSD" ]
then
	gmake -j $NUM_CPU_CORES
	echo $? > ~/install-exit-status
else
	make -j $NUM_CPU_CORES
	echo $? > ~/install-exit-status
fi

cd ~
echo "#!/bin/sh
cd cpuminer-opt-3.15.5
./cpuminer --quiet --time-limit=30 --no-color --threads=\$NUM_CPU_CORES --benchmark \$@ > \$LOG_FILE 2>&1
echo \$? > ~/test-exit-status" > cpuminer-opt
chmod +x cpuminer-opt
