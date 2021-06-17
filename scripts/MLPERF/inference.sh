# export MOBILENET_IMG_SIZE=300
# export RESNET_IMG_SIZE=1200
# cd /tmp
# git clone --recurse-submodules https://github.com/mlcommons/inference.git
# git submodule add -b branch repo_url
# export root=/tmp/inference/vision/classification_and_detection/
# cd inference/loadgen
# CFLAGS="-std=c++14" python3 setup.py develop; 
# cd /tmp/inference/vision/classification_and_detection/
# python setup.py develop
# pwd
# mkdir -p data/coco/
# cd data/coco 
# export MODEL_DIR=/tmp/inference/vision/classification_and_detection/
# export DATA_DIR=/tmp/inference/vision/classification_and_detection/data/coco
# wget http://images.cocodataset.org/zips/val2017.zip
# wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip
# unzip val2017.zip
# unzip annotations_trainval2017.zip
# cd ../..
# sh ./run_local.sh    
# pip install onnxruntime
# wget -q https://zenodo.org/record/3157894/files/mobilenet_v1_1.0_224.onnx
# pwd
# python upscale_coco.py --inputs /data/coco/ --outputs /data/coco-${MOBILENET_IMG_SIZE} --size MOBILENET_IMG_SIZE MOBILENET_IMG_SIZE --format png
# python tools/accuracy-coco.py --mlperf-accuracy-file mlperf_log_accuracy.json --coco-dir /data/coco --use-inv-map

# # # export EXTRA_OPS="--queries-offline 20 --time 10 --max-latency 0.2"
# # ./run_local.sh onnxruntime mobilenet cpu --accuracy

export MOBILENET_IMG_SIZE=300
export RESNET_IMG_SIZE=1200
cd /tmp
git clone --recurse-submodules https://github.com/mlcommons/inference.git
export root=/tmp/inference/vision/classification_and_detection/
cd inference/loadgen
CFLAGS="-std=c++14" python3 setup.py develop; 
cd /tmp/inference/vision/classification_and_detection/
python setup.py develop
export MODEL_DIR=/tmp/inference/vision/classification_and_detection/
export DATA_DIR=/tmp/inference/vision/classification_and_detection/fake_imagenet
sh tools/make_fake_imagenet.sh
pip install onnxruntime
wget -q https://zenodo.org/record/3157894/files/mobilenet_v1_1.0_224.onnx
./run_local.sh onnxruntime mobilenet cpu --accuracy