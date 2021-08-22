#!/bin/sh

unzip -o LibRaw-0.20.0-macOS.zip
tar -xf darktable-bench-assets-1.tar.bz2
chmod +x LibRaw-0.20.0/bin/postprocessing_benchmark

echo "#!/bin/sh
./LibRaw-0.20.0/bin/postprocessing_benchmark -R 50 server_room.NEF > \$LOG_FILE 2>&1
echo \$? > ~/test-exit-status" > libraw
chmod +x libraw
