#!/bin/sh
sed -i '2 i LOG_FILE=/dev/stdout' unigine-heaven
sed -i 's/OS_ARCH/(uname -i)/' unigine-heaven