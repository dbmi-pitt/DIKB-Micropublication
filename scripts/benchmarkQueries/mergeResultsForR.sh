#!/bin/bash

cat queryBenchmark.csv | grep "inferred-graph-oa-mp.xml" | cut -f4 -d\| > temp.txt

echo "------" >> temp.txt

cat queryBenchmark.csv | grep "inferred-dikb-mp-fold-1.xml" | cut -f4 -d\| >> temp.txt

echo "------" >> temp.txt

cat queryBenchmark.csv | grep "inferred-dikb-mp-fold-2.xml" | cut -f4 -d\| >> temp.txt

echo "------" >> temp.txt

cat queryBenchmark.csv | grep "inferred-dikb-mp-fold-3.xml" | cut -f4 -d\| >> temp.txt

echo "------" >> temp.txt

cat queryBenchmark.csv | grep "inferred-dikb-mp-fold-4.xml" | cut -f4 -d\| >> temp.txt

echo "------" >> temp.txt

cat queryBenchmark.csv | grep "inferred-dikb-mp-fold-5.xml" | cut -f4 -d\| >> temp.txt

echo "------" >> temp.txt

cat queryBenchmark.csv | grep "inferred-dikb-mp-fold-6.xml" | cut -f4 -d\| >> temp.txt
