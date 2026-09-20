#!/usr/bin/env python3
"""Build the gallery image set and its manifest.

Sources: the sacff-gallery zip (extracted) plus the photographs supplied
earlier. Near-duplicates are dropped so the gallery never shows the same shot
twice. Each kept photo gets a thumbnail (WebP + JPEG, so the grid is never
blank) and one larger JPEG loaded on demand by the lightbox.

Run:  python3 tools-process-gallery.py
"""
import json
import os
import subprocess
import zipfile
from pathlib import Path

from PIL import Image, ImageOps

HOME = Path.home()
ZIP = HOME / 'Downloads' / 'sacff-gallery.zip'
PREV = sorted((HOME / 'Downloads').glob('scaff-pics-*.jpeg'),
              key=lambda p: int(''.join(c for c in p.stem if c.isdigit())))
EXTRA = [HOME / 'Downloads' / 'IMG_7070.heic']

OUT = Path('assets/gallery')
WORK = Path('/private/tmp/claude-503/-Users-ukakapr-development-09172026'
            '/567e67d6-6286-4c55-8847-0458a0c43b1b/scratchpad/gal')

THUMB_EDGE, LARGE_EDGE = 620, 1500

# Written after looking at every photo — never guessed. Where a photo is simply
# the fellowship together, the alt says that rather than inventing detail.
CAPTIONS = {
    'sacff-gallery-1':  'Youth of the fellowship sharing a meal at an outdoor picnic table',
    'sacff-gallery-2':  'Children and youth gathered around a decorated cake table',
    'sacff-gallery-3':  'The fellowship together outdoors under the oak trees',
    'sacff-gallery-4':  'Musicians playing violins and cello during a service',
    'sacff-gallery-5':  'Youth in festive dress on stage before the lit cross',
    'sacff-gallery-6':  'Children and youth receiving trophies on stage',
    'sacff-gallery-7':  'Families and children at an indoor gathering',
    'sacff-gallery-8':  'Women of the fellowship together in the Texas hills',
    'sacff-gallery-9':  'The whole fellowship gathered outdoors at a park',
    'sacff-gallery-10': 'Families seated together on benches by the river',
    'sacff-gallery-11': 'Adults and children singing together on stage',
    'sacff-gallery-12': 'The fellowship out together among Christmas lights',
    'sacff-gallery-13': 'Children in nativity costumes presenting the Christmas story',
    'sacff-gallery-14': 'Children in nativity costumes with the adults who helped them',
    'sacff-gallery-15': 'The whole fellowship together in the Family Life Center',
    'sacff-gallery-16': 'The fellowship with their instruments before a festive backdrop',
    'sacff-gallery-17': 'Children dancing in festive dress during a programme',
    'sacff-gallery-18': 'Boys of the fellowship in festive dress at an evening event',
    'sacff-gallery-19': 'The congregation standing together during a service',
    'sacff-gallery-20': 'The fellowship seated together with gifts gathered for giving',
    'sacff-gallery-21': 'Singers and violinists leading worship',
    'sacff-gallery-22': "Children's song item during a programme",
    'sacff-gallery-23': 'Leaders on stage at an Indian Christian Day — Yeshu Bhakti Divas gathering',
    'sacff-gallery-24': 'The fellowship gathered in a home at Christmas',
    'sacff-gallery-25': 'Families beside the Christmas tree',
    'sacff-gallery-26': 'The fellowship together in a home with gifts to share',
    'sacff-gallery-27': 'The congregation filling the hall',
    'sacff-gallery-28': 'The fellowship singing together in a home at Christmas',
    'sacff-gallery-29': 'Families gathered by the Christmas tree',
    'scaff-pics-1':  'The choir and leaders on stage at a conference',
    'scaff-pics-4':  'Carols sung together in a living room at Christmas',
    'scaff-pics-5':  'The fellowship together outdoors at a park',
    'scaff-pics-6':  'The whole fellowship gathered in the hall',
    'scaff-pics-7':  'Children worshipping with hands raised at a Saturday service',
    'scaff-pics-8':  'Christmas gathering in a home, with Father Christmas visiting',
    'scaff-pics-10': 'The fellowship together at an anniversary celebration',
    'scaff-pics-11': 'Children presenting the nativity at a Christmas programme',
    'scaff-pics-12': 'Fellowship families visiting the local fire station at Christmas',
    'scaff-pics-14': 'The men of the fellowship at a harvest celebration',
    'scaff-pics-16': 'Members praying together in a home',
    'scaff-pics-17': 'Bible study around the tables, Bibles open',
    'scaff-pics-18': 'Children receiving awards at a special programme',
    'IMG_7070': 'The fellowship gathered on stage before the lit cross',
}

# Near-duplicates to skip: the same shot supplied twice, or a burst of frames.
SKIP = {
    'scaff-pics-13',  # identical to sacff-gallery-3
    'scaff-pics-15',  # identical to sacff-gallery-9
    'scaff-pics-2',   # near-identical to scaff-pics-1
    'scaff-pics-3',   # youth trophies — same occasion as sacff-gallery-6
    'scaff-pics-9',   # stage banner reads "TCFC-2023"
}


def unpack():
    """Extract the zip's real images, ignoring macOS resource forks."""
    WORK.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(ZIP)
    for i in z.infolist():
        name = os.path.basename(i.filename)
        if i.is_dir() or '__MACOSX' in i.filename or name.startswith('._'):
            continue
        (WORK / name).write_bytes(z.read(i))
    return sorted(WORK.glob('*.jpeg'),
                  key=lambda p: int(''.join(c for c in p.stem if c.isdigit())))


def load(src):
    """Open a source photo. Pillow has no HEIC support here, so iPhone .heic
    files are converted first with macOS's built-in `sips`."""
    if src.suffix.lower() in {'.heic', '.heif'}:
        jpg = WORK / f'{src.stem}-heic.jpg'
        if not jpg.exists():
            subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions',
                            '95', str(src), '--out', str(jpg)],
                           check=True, capture_output=True)
        src = jpg
    return ImageOps.exif_transpose(Image.open(src)).convert('RGB')


def fit(im, edge):
    w, h = im.size
    s = min(1.0, edge / max(w, h))
    return im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = unpack() + PREV + [p for p in EXTRA if p.exists()]

    manifest, skipped = [], []
    for src in sources:
        stem = src.stem
        if stem in SKIP:
            skipped.append(stem)
            continue
        im = load(src)

        thumb, large = fit(im, THUMB_EDGE), fit(im, LARGE_EDGE)
        slug = stem.replace('scaff-pics', 'photo').replace('sacff-gallery', 'g')
        thumb.save(OUT / f'{slug}-t.webp', 'WEBP', quality=78, method=6)
        thumb.save(OUT / f'{slug}-t.jpg', 'JPEG', quality=74, optimize=True)
        large.save(OUT / f'{slug}.jpg', 'JPEG', quality=76, optimize=True,
                   progressive=True)

        manifest.append({
            'slug': slug,
            'w': thumb.size[0], 'h': thumb.size[1],
            'lw': large.size[0], 'lh': large.size[1],
            'alt': CAPTIONS.get(stem, 'A photograph of the SACFF fellowship'),
        })

    Path('gallery-manifest.json').write_text(json.dumps(manifest, indent=1))

    kb = sum(f.stat().st_size for f in OUT.iterdir()) // 1024
    print(f'{len(manifest)} photos -> assets/gallery/  ({kb / 1024:.1f} MB, '
          f'{len(list(OUT.iterdir()))} files)')
    print(f'skipped as duplicates/unsuitable: {sorted(skipped)}')
    missing = [m["slug"] for m in manifest
               if m['alt'] == 'A photograph of the SACFF fellowship']
    print(f'photos without a written caption: {missing if missing else "none"}')


if __name__ == '__main__':
    main()
