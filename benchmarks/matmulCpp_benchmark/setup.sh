#!/bin/bash 

currPath=$(dirname "$0")

#if bin doesn't exist I create it
if ! [ -d $currPath/bin ]
then
    mkdir $currPath/bin
    #echo "bin directory created"
fi

if ! [ -f $currPath/bin/matmulCppExe ]
then
    FilePath=$currPath/bin #set bin as the file path

    if ! command -v g++ > /dev/null
    then
        echo "g++ compiler could not be found"
        exit 1
    fi

    #compiling the c++ code and move the executable in bin directory
    g++ $currPath/matmulCpp_benchmark.cpp -o matmulCppExe && mv matmulCppExe $FilePath
    # echo "script compiled"
fi