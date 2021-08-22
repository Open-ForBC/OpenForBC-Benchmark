#!/bin/sh

mkdir $HOME/blogbench_/

tar -zxvf blogbench-1.1.tar.gz
cd blogbench-1.1/

if [ $OS_ARCH = "aarch64" ]
then
	./configure --build=arm --prefix=$HOME/blogbench_/
else
	./configure --prefix=$HOME/blogbench_/
fi

make -j $NUM_CPU_CORES
echo $? > ~/install-exit-status
make install
cd ~
rm -rf blogbench-1.1/

echo "#!/bin/sh
rm -rf \$HOME/scratch/
mkdir \$HOME/scratch/
./blogbench_/bin/blogbench -d \$HOME/scratch > \$LOG_FILE 2>&1
echo \$? > ~/test-exit-status
rm -rf \$HOME/scratch/" > blogbench
chmod +x blogbench
