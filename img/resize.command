#!/bin/bash

cd "$(dirname "$0")"

mogrify -resize 768x768 *.png

echo "완료: PNG 이미지가 768x768로 리사이즈되었습니다."
read -p "엔터 누르면 종료"

