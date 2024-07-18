#!/bin/bash

cd requirements/

# requirements.txt 파일 생성
poetry export --format=requirements.txt --output=common.txt --without-hashes --without=dev --without=prob --without=test -q &

# requirements.dev.txt 파일 생성
poetry export --format=requirements.txt --output=dev.txt --without-hashes --only=dev -q &

# requirements.prob.txt 파일 생성
poetry export --format=requirements.txt --output=prob.txt --without-hashes --only=prob -q &

# requirements.test.txt 파일 생성
poetry export --format=requirements.txt --output=test.txt --without-hashes --only=test -q &

# 백그라운드에서 실행 중인 모든 작업이 완료될 때까지 기다림
wait

# 조건부 종속성 제거
sed -i 's/;.*//' common.txt
sed -i 's/;.*//' dev.txt
sed -i 's/;.*//' prob.txt
sed -i 's/;.*//' test.txt

echo "All exports completed."