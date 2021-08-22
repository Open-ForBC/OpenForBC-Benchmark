#!/bin/sh

7z x Bosphorus_1920x1080_120fps_420_8bit_YUV_RAW.7z
cp SvtVp9EncApp-0.1.exe SvtVp9EncApp.exe
cp SvtVp9Enc-0.1.dll SvtVp9Enc.dll
chmod +x SvtVp9EncApp.exe

echo "#!/bin/sh
./SvtVp9EncApp.exe \$@ > \$LOG_FILE 2>&1" > svt-vp9
chmod +x svt-vp9
