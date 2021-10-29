#!/bin/bash 

currPath=$(dirname "$0")
# python modules installation
if ! pip install -r $currPath/requirements.txt
then
    echo "Required modules installed"
fi

#LOOK AT CUDA VERSION AND INSTALL TORCH
CUDA_VER=$(nvidia-smi | grep -oP  '(?<=CUDA Version: )[0-9]*')
re='^[0-9]+$'   

if ! [[ $CUDA_VER =~ $re ]]
then
    echo 'CUDA not installed, please manually install it.'
elif CUDA_VER==11
then
    pip install torch==1.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
else
    pip install torch
fi