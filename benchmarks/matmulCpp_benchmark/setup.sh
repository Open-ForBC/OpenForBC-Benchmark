currPath=$(dirname "$0")
#echo $currPath

#if bin exist I delete it
# if [ -d $currPath/bin ]
# then
#     rm -r $currPath/bin
#     echo "bin directory deleted"
# fi

#if bin doesn't exist I create it
if ! [ -d $currPath/bin ]
then
    mkdir $currPath/bin
    #echo "bin directory created"
fi

if ! [ -f $currPath/bin/matmulCppExe ]
then
    FilePath=$currPath/bin #set bin as the file path

    g++ $currPath/matmulCpp.cpp -o matmulCppExe #compiling the c++ code
    mv matmulCppExe $FilePath #move the executable in bin directory
    #echo "script compiled"
fi