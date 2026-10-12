"""Check that every published LOAD uses one of the two matching shared schemas."""
from html.parser import HTMLParser
from pathlib import Path
import csv
import re

root = Path(__file__).resolve().parents[1]
class Codes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.snippets = []
    def handle_starttag(self, tag, attrs):
        if tag == 'code' and dict(attrs).get('data-language') == 'pig':
            self.active = True
            self.snippets.append('')
    def handle_endtag(self, tag):
        if tag == 'code':
            self.active = False
    def handle_data(self, data):
        if self.active:
            self.snippets[-1] += data

parser = Codes()
parser.feed((root / 'index.html').read_text())
files = {p.name: list(csv.reader(p.open())) for p in (root / 'inputs').glob('*.txt')}
assert set(files) == {'data1.txt', 'data2.txt'}
assert len(parser.snippets) == 22
used = set()
for code in parser.snippets:
    loads = re.findall(r"LOAD '([^']+)' USING PigStorage\(','\)\s+AS \(([^)]+)\)", code)
    assert loads, code
    for filename, schema in loads:
        used.add(filename)
        fields = [field.strip().split(':') for field in schema.split(',')]
        for row in files[filename]:
            assert len(row) == len(fields), (filename, row, fields)
            for value, (_, dtype) in zip(row, fields):
                if dtype == 'int':
                    int(value)
assert used == set(files)
assert 'temp != 9999' in parser.snippets[14]
assert 'm1 + m2 + m3' in parser.snippets[17]
print('22 Pig programs use exactly two files with matching typed schemas.')
