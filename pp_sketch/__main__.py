# Copyright 2019 John Lees

'''Wrapper around sketch functions'''

import os, sys

import numpy as np
import h5py

import pp_sketchlib

from .__init__ import __version__

def get_options():
    import argparse

    description = 'Run poppunk sketching/distances'
    parser = argparse.ArgumentParser(description=description,
                                     prog='pp_sketch')

    modeGroup = parser.add_argument_group('Mode of operation')
    mode = modeGroup.add_mutually_exclusive_group(required=True)
    mode.add_argument('--sketch',
                        action='store_true',
                        default=False,
                        help='Create a database of sketches')
    mode.add_argument('--query',
                        action='store_true',
                        default=False,
                        help='Find distances between two sketch databases')

    io = parser.add_argument_group('Input/output')
    io.add_argument('--rfile',
                    help='Samples to sketch')
    io.add_argument('--ref-db',
                    help='Prefix of reference database file')
    io.add_argument('--query-db',
                    help='Prefix of query database file')

    kmerGroup = parser.add_argument_group('Kmer comparison options')
    kmerGroup.add_argument('--min-k', default = 13, type=int, help='Minimum kmer length [default = 13]')
    kmerGroup.add_argument('--max-k', default = 29, type=int, help='Maximum kmer length [default = 29]')
    kmerGroup.add_argument('--k-step', default = 4, type=int, help='K-mer step size [default = 4]')
    kmerGroup.add_argument('--sketch-size', default=32, type=int, help='Kmer sketch size [default = 32]')

    other = parser.add_argument_group('Other')
    other.add_argument('--cpus',
                        type=int,
                        default=1,
                        help='Number of CPUs to use '
                             '[default = 1]')
    other.add_argument('--version', action='version',
                       version='%(prog)s '+__version__)

    return parser.parse_args()


def main():
    args = get_options()

    if args.min_k >= args.max_k or args.min_k < 9 or args.max_k > 31 or args.k_step < 2:
        sys.stderr.write("Minimum kmer size " + str(args.min_k) + " must be smaller than maximum kmer size " +
                         str(args.max_k) + "; range must be between 9 and 31, step must be at least one\n")
        sys.exit(1)
    kmers = np.arange(args.min_k, args.max_k + 1, args.k_step)

    if args.sketch:
        names = []
        sequences = []
        
        with open(args.rfile, 'rU') as refFile:
            for refLine in refFile:
                name, sequence = refLine.rstrip().split("\t")
                names.append(name)
                sequences.append(sequence)

        pp_sketchlib.constructDatabase(args.ref_db, names, sequences, kmers, args.sketch_size, args.cpus)

    elif args.query:
        # TODO: add option to get names from HDF5 files
        rList = []
        ref = h5py.File(args.ref_db, 'r')
        for sample_name in list(ref['sketches'].keys()):
            rList.append(sample_name)

        qList = []
        query = h5py.File(args.query_db, 'r')
        for sample_name in list(query['sketches'].keys()):
            qList.append(sample_name)

        distMat = pp_sketchlib.queryDatabase(args.ref_db, args.query_db, rList, qList, kmers, args.cpus)
          
        print(distMat)

    sys.exit(0)

if __name__ == "__main__":
    main()