import codecs
import csv
import json
import re

import requests

ENTRIES_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6mTxZKu1-45eMd7tdWuxoiH_c0ImtXO0rvjJNqkgvoe7CJ1kDArbVtKYNC1U4s2UnZTjmTzr2FRA1/pub?gid=0&single=true&output=csv'
RINGS_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6mTxZKu1-45eMd7tdWuxoiH_c0ImtXO0rvjJNqkgvoe7CJ1kDArbVtKYNC1U4s2UnZTjmTzr2FRA1/pub?gid=1055220400&single=true&output=csv'
QUADRANTS_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6mTxZKu1-45eMd7tdWuxoiH_c0ImtXO0rvjJNqkgvoe7CJ1kDArbVtKYNC1U4s2UnZTjmTzr2FRA1/pub?gid=1460082809&single=true&output=csv'

TARGET_HTML = 'docs/index.html'
MARKER_START = '/* RADAR START */'
MARKER_END = '/* RADAR END */'


def iter_csv(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return csv.DictReader(response.iter_lines(decode_unicode=True))


def main():
    # Quadrants
    quadrants = []
    quadrant_to_index = {}
    for row in iter_csv(QUADRANTS_CSV):
        quadrants.append({'name': row['Name']})
        quadrant_to_index[row['Name']] = len(quadrants) - 1

    # Rings
    rings = []
    ring_to_index = {}
    for row in iter_csv(RINGS_CSV):
        rings.append({'name': row['Name'].upper(), 'color': row['Colour']})
        ring_to_index[row['Name']] = len(rings) - 1

    # Entries
    entries = []
    for row in iter_csv(ENTRIES_CSV):
        entries.append({
            'quadrant': quadrant_to_index[row['Quadrant']],
            'ring': ring_to_index[row['Ring']],
            'label': row['Name'],
        })

    radar_config = {
        'svg_id': 'radar',
        'width': 1450,
        'height': 1000,
        'colors': {
            'background': "#fff",
            'grid': "#bbb",
            'inactive': "#ddd"
        },
        'title': "Yoyo Wallet Tech Radar — 2019.02",
        'print_layout': True,
        'quadrants': quadrants,
        'rings': rings,
        'entries': entries,
    }

    with open(TARGET_HTML, 'r') as f:
        html = f.read()

    html = re.sub(
        f'({re.escape(MARKER_START)}).*({re.escape(MARKER_END)})',
        r'\1' + json.dumps(radar_config).replace('\\', r'\\') + r'\2',
        html,
    )

    with open(TARGET_HTML, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
