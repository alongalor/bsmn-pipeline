#!/shared/apps/pyenv/versions/3.6.2/bin/python

import argparse
import re
import subprocess
import sys
from scipy.stats import binom_test 
from library.utils import coroutine, printer
from library.pileup import pileup, clean, count

def run(args):
    v_info = vaf_info(pileup(args.bam, args.min_MQ, args.min_BQ, clean(count())))
    header = ('#chr\tpos\tref\talt\tvaf\t'
            + 'depth\tref_n\talt_n\tp_binom')
    printer(header)
    for snv in args.infile:
        if snv[0] == '#':
            continue
        chrom, pos, ref, alt = snv.strip().split()[:4]
        printer('{chrom}\t{pos}\t{ref}\t{alt}\t{vaf_info}'.format(
            chrom=chrom, pos=pos, ref=ref.upper(), alt=alt.upper(), 
            vaf_info=v_info.send((chrom, pos, ref, alt))))

@coroutine
def vaf_info(target):
    result = None
    while True:
        chrom, pos, ref, alt = (yield result)
        base_n = target.send((chrom, pos))
        depth = sum(base_n.values())
        ref_n = base_n[ref.upper()] + base_n[ref.lower()]
        alt_n = base_n[alt.upper()] + base_n[alt.lower()]
        try:
            vaf = alt_n/depth
        except ZeroDivisionError:
            vaf = 0
            
        result = '{vaf:f}\t{depth}\t{ref_n}\t{alt_n}\t{p_binom:e}'.format(
            vaf=vaf, depth=depth, ref_n=ref_n, alt_n=alt_n, p_binom=binom_test(alt_n, depth))

def main():
    parser = argparse.ArgumentParser(
        description='Test whether VAF of each SNV is somatic or germline.')

    parser.add_argument(
        '-b', '--bam', metavar='FILE',
        help='bam file',
        required=True)

    parser.add_argument(
        '-q', '--min-MQ', metavar='INT',
        help='mapQ cutoff value [20]',
        type=int, default=20)

    parser.add_argument(
        '-Q', '--min-BQ', metavar='INT',
        help='baseQ/BAQ cutoff value [13]',
        type=int, default=13)
    
    parser.add_argument(
        'infile', metavar='snv_list.txt',
        help='''SNV list.
        Each line format is "chr\\tpos\\tref\\talt".
        Trailing columns will be ignored. [STDIN]''',
        nargs='?', type=argparse.FileType('r'),
        default=sys.stdin)

    parser.set_defaults(func=run)
    
    args = parser.parse_args()

    if(len(vars(args)) == 0):
        parser.print_help()
    else:
        args.func(args)
        
if __name__ == "__main__":
    main()
