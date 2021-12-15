#!/bin/bash 

currPath=$(dirname "$0")
## PYTHON MODULES INSTALLATION ##
if ! pip install -r $currPath/requirements.txt
then
    echo "Required modules installed"
fi

## CHECK THE PRESENCE OF A CUDA VERSION ##
CUDA_VER=$(nvidia-smi | grep -oP  '(?<=CUDA Version: )[0-9]*')
re='^[0-9]+$'   

if ! [[ $CUDA_VER =~ $re ]]
then
    echo 'CUDA not installed, please manually install it.'
fi