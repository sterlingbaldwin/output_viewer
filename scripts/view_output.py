#!/usr/bin/env python

from argparse import ArgumentParser
from output_viewer.build import build_viewer

parser = ArgumentParser(description="Generate HTML pages for viewing output.")
parser.add_argument('path', help="Path to index file for output.", default="index.json", nargs="?")
parser.add_argument('--dataset', help="Name of your output", default="AIMS Output Viewer")


args = parser.parse_args()
build_viewer(args.path, args.dataset)
