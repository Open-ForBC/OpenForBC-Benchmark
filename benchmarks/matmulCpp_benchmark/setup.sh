currPath=$(pwd)  

# if [ -d $currPath/bin ]
# then
#     echo "removing bin directory"
#     rm -r bin
# fi

if ! [ -d $currPath/bin ]  #if bin doesn't exist I create it
then
    echo "creating bin directory"
    mkdir bin
fi

FilePath=$currPath/bin #set bin as the file path

g++ matmulCpp.cpp -o matmulCppExe #compiling the c++ code
smv matmulCppExe $FilePath #move the executable in bi directory
 