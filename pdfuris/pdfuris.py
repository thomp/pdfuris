#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# pdfuris.py: try to grab URIs in a PDF
#

import argparse
import json
import PyPDF2
import sys

import logging
import logging.config
# define LG as the generic logger
lg = logging
# and immediately configure the logger format
log_format = '%(message)s'
lg.basicConfig(format=log_format,stream=sys.stdout)

def extract_uris(input_pdf_file):
    reader = PyPDF2.PdfFileReader(input_pdf_file)
    uris = []
    for page_number in range(reader.getNumPages()):
        print "Page number", page_number
        page_object = reader.getPage(page_number)
        obj = page_object.getObject()
        annots = obj.get('/Annots', [])
        # annots may be
        # - iterable
        # - a PyPDF2.generic.IndirectObject instance (not iterable)
        if isinstance(annots,PyPDF2.generic.IndirectObject):
            extract_uris_from_indirect_object(annots,uris,0)
        else:
            for annot_object in annots:
                u = annot.getObject()
                uri = u['/A'].get('/URI')
                if uri:
                    uris.append(uri)
    return uris

def extract_uris_from_indirect_object (indirect_obj,uris,n):
    # indirect object may contain a bunch of nested IndirectObject objects
    n = n+1
    if (n>1000):
        print "Too deep"
        exit
    maybe_iterable = indirect_obj.getObject()
    if might_be_iterable(maybe_iterable):
        extract_uris_from_iterable (maybe_iterable,uris)
    else:
        # assume, if it's not iterable, it's an IndirectObject instance
        extract_uris_from_indirect_object (iterable_obj,uris,n)

def extract_uris_from_iterable (iterable_obj,uris):
    for obj in iterable_obj:
        x = obj.getObject()
        # x might
        # - have type \Annot
        # - in which case, /A is of interest if it has /URI
        uri = x['/A'].get('/URI')
        if uri:
            uris.append(uri)

def might_be_iterable (x):
    try:
        iter(x)
        return True
    except TypeError:
        return False

def main():
    """Handle command-line invocation."""
    parser = argparse.ArgumentParser(description="This is pdfuris")
    parser.add_argument("input_files", help="an input (PDF) file",
                        nargs=1,
                        type=str)
    args = parser.parse_args()
    pdf_file_spec = args.input_files[0]
    try:
        print json.dumps(extract_uris(pdf_file_spec))
    except Exception as e:
        lg.error("Crash and burn")
        lg.error(sys.exc_info()[0])
        raise

if __name__ == "__main__":
    main()
