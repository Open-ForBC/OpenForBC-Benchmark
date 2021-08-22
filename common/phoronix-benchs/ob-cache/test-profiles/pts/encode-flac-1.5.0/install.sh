#!/bin/sh

mkdir $HOME/flac_
tar -xJf flac-1.3.1.tar.xz

cd flac-1.3.1/
./configure --prefix=$HOME/flac_
make -j $NUM_CPU_JOBS
echo $? > ~/install-exit-status
make install
cd ~
rm -rf flac-1.3.1/
rm -rf flac_/share/

echo "#!/bin/sh
./flac_/bin/flac --best \$TEST_EXTENDS/pts-trondheim.wav -f -o /dev/null 2>&1
./flac_/bin/flac --best \$TEST_EXTENDS/pts-trondheim.wav -f -o /dev/null 2>&1
./flac_/bin/flac --best \$TEST_EXTENDS/pts-trondheim.wav -f -o /dev/null 2>&1
echo \$? > ~/test-exit-status" > encode-flac
chmod +x encode-flac
