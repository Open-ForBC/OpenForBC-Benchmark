cd /tmp
git clone https://github.com/mlcommons/training.git
cd training/image_segmentation/pytorch
docker build -t unet3d .
mkdir raw-data-dir
cd raw-data-dir
git clone https://github.com/neheller/kits19
cd kits19
pip3 install -r requirements.txt
python3 -m starter_code.get_imaging
mkdir data
mkdir results
docker run --ipc=host -it --rm --runtime=nvidia -v RAW-DATA-DIR:/raw_data -v PREPROCESSED-DATA-DIR:/data -v RESULTS-DIR:/results unet3d:latest /bin/bash

