#!/bin/bash
#$ -cwd
#$ -pe threaded 4

trap "exit 100" ERR

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename $0) [sample name] [file name]"
    false
fi

SM=$1
FNAME=$2

source $(pwd)/$SM/run_info

set -o nounset
set -o pipefail

printf -- "---\n[$(date)] Start bam2fastq: $FNAME\n"

FSIZE=$(stat -c%s $SM/downloads/$FNAME)

if [[ $(($FSIZE/1024**3)) -lt 128 ]]; then
    TMP_N=128
elif [[ $(($FSIZE/1024**3)) -lt 1000 ]]; then
    TMP_N=$(($FSIZE/1024**3+1))
else
    echo "The bam file is bigger than 1TB."
    exit 1
fi
    
mkdir -p $SM/fastq
$SAMTOOLS collate -uOn $TMP_N $SM/downloads/$FNAME $SM/$FNAME.collate \
    |$SAMTOOLS fastq -F 0x900 -1 $SM/fastq/$FNAME.R1.fastq.gz -2 $SM/fastq/$FNAME.R2.fastq.gz -
rm $SM/downloads/$FNAME

printf -- "[$(date)] Finish bam2fastq: $FNAME\n---\n"
