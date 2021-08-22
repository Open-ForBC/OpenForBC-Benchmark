#!/bin/sh

tar -xf xmrig-6.12.1.tar.gz 
cd xmrig-6.12.1

# Make the benchmark quit when done (after printing benchmark finished result)
sed -i '136 i exit(0);' src/base/net/stratum/benchmark/BenchClient.cpp

mkdir build
cd build

cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_OPENCL=OFF -DWITH_CUDA=OFF

if [ "$OS_TYPE" = "BSD" ]
then
	gmake -j $NUM_CPU_CORES
	echo $? > ~/install-exit-status
else
	make -j $NUM_CPU_CORES
	echo $? > ~/install-exit-status
fi

cd ~

echo "#!/bin/sh
cd xmrig-6.12.1/build
./xmrig --no-color --threads=\$NUM_CPU_CORES \$@ -l \$LOG_FILE
echo \$? > ~/test-exit-status" > xmrig
chmod +x xmrig
