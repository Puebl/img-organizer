import argparse
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags
from tqdm import tqdm

EXIF_DATETIME_KEYS = {36867, 306}  # DateTimeOriginal, DateTime


def exif_datetime(p: Path) -> datetime | None:
    try:
        with Image.open(p) as img:
            info = img.getexif()
            for k in EXIF_DATETIME_KEYS:
                v = info.get(k)
                if v:
                    try:
                        # formats: 'YYYY:MM:DD HH:MM:SS'
                        return datetime.strptime(str(v), "%Y:%m:%d %H:%M:%S")
                    except Exception:
                        pass
    except Exception:
        return None
    return None


def file_datetime(p: Path) -> datetime:
    dt = exif_datetime(p)
    if dt:
        return dt
    return datetime.fromtimestamp(p.stat().st_mtime)


def sha1sum(p: Path) -> str:
    h = hashlib.sha1()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def organize(src: Path, dst: Path, dedupe: bool):
    dst.mkdir(parents=True, exist_ok=True)
    seen_hashes: set[str] = set()

    files = [p for p in src.rglob('*') if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff'}]
    for p in tqdm(files, desc="Organizing"):
        try:
            dt = file_datetime(p)
            out_dir = dst / f"{dt.year:04d}" / f"{dt.month:02d}" / f"{dt.day:02d}"
            out_dir.mkdir(parents=True, exist_ok=True)

            if dedupe:
                h = sha1sum(p)
                if h in seen_hashes:
                    continue
                seen_hashes.add(h)

            target = out_dir / p.name
            # avoid overwrite
            i = 1
            stem = p.stem
            while target.exists():
                target = out_dir / f"{stem}_{i}{p.suffix}"
                i += 1
            shutil.copy2(p, target)
        except Exception as e:
            print(f"[WARN] {p}: {e}")


def main():
    ap = argparse.ArgumentParser(description="Organize images by date")
    ap.add_argument('--src', required=True)
    ap.add_argument('--dst', required=True)
    ap.add_argument('--dedupe', action='store_true')
    args = ap.parse_args()

    organize(Path(args.src), Path(args.dst), args.dedupe)

if __name__ == '__main__':
    main()
