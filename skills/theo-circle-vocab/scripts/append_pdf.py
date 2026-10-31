#!/usr/bin/env python3
"""Append a prepared vocabulary batch to a PDF without overwriting the source."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def page_signature(page):
    return (tuple(float(x) for x in page.mediabox), page.extract_text() or '')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--batch', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    base = args.base.resolve(strict=True)
    batch = args.batch.resolve(strict=True)
    output = args.output.resolve()
    if output in (base, batch):
        parser.error('Output must be a separate file so the originals remain intact.')
    old = PdfReader(base)
    new = PdfReader(batch)
    if old.is_encrypted or new.is_encrypted:
        parser.error('Encrypted PDFs are not supported by this helper.')
    if not old.pages or not new.pages:
        parser.error('Both input files must contain at least one page.')
    signatures = [page_signature(p) for p in old.pages] + [page_signature(p) for p in new.pages]
    writer = PdfWriter()
    writer.append(old)
    writer.append(new)
    if old.metadata:
        metadata = {str(k): str(v) for k, v in old.metadata.items() if v is not None}
        writer.add_metadata(metadata)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('wb') as fp:
        writer.write(fp)
    check = PdfReader(output)
    if [page_signature(p) for p in check.pages] != signatures:
        output.unlink(missing_ok=True)
        raise RuntimeError('Page content or dimensions changed while appending.')
    print(json.dumps({'old_pages':len(old.pages), 'added_pages':len(new.pages), 'total_pages':len(check.pages), 'output':str(output)},ensure_ascii=False))


if __name__ == '__main__':
    main()
