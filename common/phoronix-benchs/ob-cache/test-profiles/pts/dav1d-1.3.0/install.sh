#!/bin/sh

# FFmpeg install to demux AV1 WebM to IVF that can then be consumed by dav1d...
tar -xjf ffmpeg-4.2.1.tar.bz2
mkdir ffmpeg_/

cd ffmpeg-4.2.1/
./configure --disable-zlib --disable-doc --prefix=$HOME/ffmpeg_/
make -j $NUM_CPU_CORES
echo $? > ~/install-exit-status
make install
cd ~/

./ffmpeg_/bin/ffmpeg -i Stream2_AV1_HD_6.8mbps.webm -vcodec copy -an -f ivf summer_nature_1080p.ivf
rm Stream2_AV1_HD_6.8mbps.webm
./ffmpeg_/bin/ffmpeg -i Stream2_AV1_4K_22.7mbps.webm -vcodec copy -an -f ivf summer_nature_4k.ivf
rm Stream2_AV1_4K_22.7mbps.webm
./ffmpeg_/bin/ffmpeg -i Chimera-AV1-8bit-1920x1080-6736kbps.mp4 -vcodec copy -an -f ivf chimera_8b_1080p.ivf
rm Chimera-AV1-8bit-1920x1080-6736kbps.mp4
./ffmpeg_/bin/ffmpeg -i Chimera-AV1-10bit-1920x1080-6191kbps.mp4 -vcodec copy -an -f ivf chimera_10b_1080p.ivf
rm Chimera-AV1-10bit-1920x1080-6191kbps.mp4

rm -rf ffmpeg-4.2.1
rm -rf ffmpeg_

# Build Dav1d
tar -xf dav1d-0.4.0.tar.xz
cd dav1d-0.4.0
meson build --buildtype release
ninja -C build
echo $? > ~/install-exit-status

cd ~

echo "#!/bin/sh
./dav1d-0.4.0/build/tools/dav1d \$@ --muxer null --framethreads \$NUM_CPU_CORES --tilethreads 4 --filmgrain 0 > \$LOG_FILE 2>&1
echo \$? > ~/test-exit-status" > dav1d
chmod +x dav1d
