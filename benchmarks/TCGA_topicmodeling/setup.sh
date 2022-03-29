#!/bin/bash 

currPath=$(dirname "$0")
## PYTHON MODULES INSTALLATION ##
python3 -m pip install -U pip
python3 -m pip install -r $currPath/requirements.txt

if [ -e $currPath/breast_cancer.tar.gz ]
then
    gunzip $currPath/breast_cancer.tar.gz
    tar -xvf $currPath/breast_cancer.tar
else
    curl -X GET https://raw.githubusercontent.com/fvalle1/OpenForBC-Benchmark/develop/benchmarks/TCGA_topicmodeling/breast_cancer.tar.gz --output breast_cancer.tar.gz
    gunzip $currPath/breast_cancer.tar.gz
    tar -xvf $currPath/breast_cancer.tar
fi

rm -f $currPath/breast_cancer.tar
