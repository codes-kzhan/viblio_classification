#!/bin/bash

# ./video_classifier.sh ~/data/videos/vid4.mp4 ~/data/working_dir ~/data/model_dir

cur_dir=$(pwd)
export LD_LIBRARY_PATH="$cur_dir"/../../src/vl_feat/vlfeat-0.9.16/bin/glnxa64:$LD_LIBRARY_PATH


# get path to input video
if [ "$1" != "" ] && [ "$2" != "" ] && [ "$3" != "" ]; then
    video_file=$1
    working_dir=$2
    model_dir=$3
else
    echo "Use ./video_classifier.sh input_file working_dir"
    echo "input_file: path to the input video h.264 encoded"
    echo "working_dir:path where temporary output features and files are stored"
    echo "model_dir: path to the directory containing:"
    echo "  svm_default.model : model trained using svm"
    echo "  svm_config.cfg : svm config file"
    echo "  /frames : a directory that will be used to store frames extracted from input video."
    echo "  /features : a directory that will be used to store features extracted from video frames."
    exit -1
fi

feature_dir="$working_dir"/features
frames_dir="$working_dir"/frames_dir
svm_model_file="$model_dir"/svm_default.model
svm_config_file="$model_dir"/svm_config.cfg


# check if working directory exists
if [ -d "$working_dir" ]; then
    if [ ! -d "$feature_dir" ]; then
        mkdir $feature_dir
    fi
    if [ ! -d "$frames_dir" ]; then
        mkdir $frames_dir
    fi
else
    echo "working directory does not exist."
    exit -1
fi

if [ ! -d "$model_dir" ];then
    echo "model directory doesn't exist"
    exit -1
fi
#extract the base name of video
filename=$(basename "$video_file" ".mp4")
#chop the file extension
name=${filename%.*}
#extract frames
rm -f "$frames_dir"/"$name"*
# extract a frame every 5 seconds. -r = 1/5 =0.2
ffmpeg -i $video_file -r 0.4 -f image2 "$frames_dir"/"$name"_images%05d.png > /dev/null 2>&1
#ffmpeg -i $video_file -r 0.4 -f image2 "$frames_dir"/"$name"_images%05d.png

#create input for feature extractor
path_file="$frames_dir"/"$name"_path.txt
#rm -f $path_file
for entry in "$frames_dir"/"$name"*
do
  echo $frames_dir $(basename "$entry") label 0 >> "$path_file"
done

python feature_extractor.py -i $path_file -o $name -inter_dir $feature_dir > /dev/null 2>&1
#python feature_extractor.py -i $path_file -o $name -inter_dir $feature_dir
python viblio_classifier.py -d $feature_dir -i "$name"_features.txt -m $svm_model_file -p "$feature_dir"/"$name"_predict.txt -c $svm_config_file -s predict -a > /dev/null 2>&1
#python viblio_classifier.py -d $feature_dir -i "$name"_features.txt -m $svm_model_file -p "$feature_dir"/"$name"_predict.txt -c $svm_config_file -s predict -a

res=$(python aggregate_frame_labels.py -i "$feature_dir"/"$name"_predict.txt)
detected=$(python -c "print 'yes' if $res > 0.6 else 'no'")


case "$feature_dir" in 
    /mnt*) 
            rm -r $feature_dir > /dev/null 2>&1;;
       
esac

case "$frames_dir" in 
    /mnt*) 
            rm -r $frames_dir > /dev/null 2>&1;;
       
esac

if [ $detected == 'yes' ]
then
    echo $res
    exit 1
else
    echo $res
    exit 0
fi

