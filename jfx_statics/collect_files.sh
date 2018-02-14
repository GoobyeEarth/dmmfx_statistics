#!/usr/bin/env bash

max_num=$1
input_dir=$2
output_file=$3

for num in `seq ${max_num}`
do
echo "tail -n +4 files/${input_dir}/${num}.csv >| files/${output_file}"
tail -n +4 ${input_dir}/${num}.csv >> ${output_file}
done