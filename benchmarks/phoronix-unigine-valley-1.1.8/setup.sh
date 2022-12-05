#!/bin/sh
sed -i '2 i LOG_FILE=/dev/stdout' unigine-valley
sed -i 's/OS_ARCH/(uname -i)/' unigine-valley