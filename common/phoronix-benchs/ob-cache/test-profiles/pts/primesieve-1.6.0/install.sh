#!/bin/sh

version=7.2
tar xvf primesieve-$version.tar.gz
cd primesieve-$version

cmake . -DBUILD_SHARED_LIBS=OFF
make -j $NUM_CPU_JOBS
echo $? > ~/install-exit-status
cd ..

echo "#!/bin/sh
primesieve-$version/./primesieve \$@ > \$LOG_FILE 2>&1
echo \$? > ~/test-exit-status" > primesieve-test
chmod +x primesieve-test
