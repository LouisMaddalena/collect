#!/usr/bin/env python3
import argparse
from pathlib import Path
import shutil
from datetime import date as _date

try:
    import yaml  # pip install pyyaml
    _HAVE_YAML = True
except Exception:
    _HAVE_YAML = False


def log(msg, verbose=False):
    if verbose:
        print(msg)


# ---------- Discovery ----------

TXT_NAMES = ("collect.txt", ".collect.txt")
YAML_NAMES = (
    "collect.yaml", ".collect.yaml",
    "collect.yml", ".collect.yml",
)

def _collect_file_in_dir(d: Path):
    """Return the highest-priority collect file in a dir, preferring hidden and YAML."""
    # Prefer hidden YAML, then visible YAML, then hidden txt, then visible txt
    prefs = [
        ".collect.yaml", ".collect.yml",
        "collect.yaml", "collect.yml",
        ".collect.txt", "collect.txt",
    ]
    for name in prefs:
        p = d / name
        if p.exists():
            return p
    return None

def find_collect_files(root: Path):
    root = root.resolve()
    for p in root.rglob("*"):
        if p.is_dir():
            f = _collect_file_in_dir(p)
            if f is not None:
                yield f


# ---------- Parsing ----------

def _validate_iso_date(s: str) -> str | None:
    try:
        _ = _date.fromisoformat(s)
        return s
    except Exception:
        return None

def _normalize_categories(categories):
    if categories is None:
        return []
    if isinstance(categories, str):
        parts = [c.strip() for c in categories.split(",")]
    elif isinstance(categories, (list, tuple)):
        parts = [str(c).strip() for c in categories]
    else:
        parts = []
    # dedupe, preserve order
    seen, out = set(), []
    for c in parts:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out

def parse_txt(f: Path, verbose=False):
    date_val = None
    categories = []
    try:
        with f.open("r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                lower = line.lower()
                if lower.startswith("date:"):
                    date_val = line.split(":", 1)[1].strip()
                elif lower.startswith("category:"):
                    cats = line.split(":", 1)[1].strip()
                    categories.extend([c.strip() for c in cats.split(",") if c.strip()])
    except Exception as e:
        print(f"ERROR reading {f}: {e}")
        return None, []

    if date_val:
        iso = _validate_iso_date(date_val)
        if not iso:
            print(f"WARNING {f}: invalid ISO date '{date_val}'. Expected YYYY-MM-DD. Skipping date.")
            date_val = None

    cats = _normalize_categories(categories)
    log(f"Parsed (txt) {f}: Date={date_val}, Categories={cats}", verbose)
    return date_val, cats

def parse_yaml(f: Path, verbose=False):
    if not _HAVE_YAML:
        print(f"WARNING: {f} is YAML but PyYAML not installed. `pip install pyyaml` to enable.")
        return None, []
    try:
        with f.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as e:
        print(f"ERROR reading YAML {f}: {e}")
        return None, []

    date_val = data.get("date")
    if date_val:
        iso = _validate_iso_date(str(date_val))
        if not iso:
            print(f"WARNING {f}: invalid ISO date '{date_val}'. Expected YYYY-MM-DD. Skipping date.")
            date_val = None

    cats = _normalize_categories(data.get("categories"))
    log(f"Parsed (yaml) {f}: Date={date_val}, Categories={cats}", verbose)
    return date_val, cats


def parse_collect_file(f: Path, verbose=False):
    if f.name in YAML_NAMES:
        return parse_yaml(f, verbose)
    return parse_txt(f, verbose)


# ---------- Indexing ----------

def ensure_dir(p: Path, dry_run=False, verbose=False):
    if dry_run:
        log(f"[dry-run] mkdir -p {p}", verbose)
        return
    p.mkdir(parents=True, exist_ok=True)

def make_symlink(link_path: Path, target: Path, *, force=False, dry_run=False, verbose=False):
    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink():
            try:
                current = link_path.resolve()
            except Exception:
                current = None
            if current == target.resolve():
                log(f"Link ok: {link_path} -> {target}", verbose)
                return
        if not force:
            log(f"Exists (use --force to replace): {link_path}", verbose)
            return
        if dry_run:
            log(f"[dry-run] rm -rf {link_path}", verbose)
        else:
            if link_path.is_dir() and not link_path.is_symlink():
                shutil.rmtree(link_path)
            else:
                link_path.unlink(missing_ok=True)

    if dry_run:
        log(f"[dry-run] ln -s {target} {link_path}", verbose)
        return
    try:
        link_path.symlink_to(target, target_is_directory=True)
        log(f"Symlink created: {link_path} -> {target}", verbose)
    except OSError as e:
        print(f"ERROR creating symlink {link_path} -> {target}: {e}")

def index_entry(collect_root: Path, source_dir: Path, date_str: str | None, categories,
                *, force=False, dry_run=False, verbose=False, group_dates=False):
    # Category links
    for cat in categories:
        target_dir = collect_root / "Category" / cat
        ensure_dir(target_dir, dry_run, verbose)
        link = target_dir / source_dir.name
        make_symlink(link, source_dir, force=force, dry_run=dry_run, verbose=verbose)

    # Date links
    if date_str:
        if group_dates:
            y, m, d = date_str.split("-")
            target_dir = collect_root / "Date" / y / m / d
        else:
            target_dir = collect_root / "Date" / date_str
        ensure_dir(target_dir, dry_run, verbose)
        link = target_dir / source_dir.name
        make_symlink(link, source_dir, force=force, dry_run=dry_run, verbose=verbose)

def remove_indexes(collect_root: Path, *, dry_run=False, verbose=False):
    for sub in ("Date", "Category"):
        p = collect_root / sub
        if p.exists():
            if dry_run:
                log(f"[dry-run] rm -rf {p}", verbose)
            else:
                shutil.rmtree(p)
                log(f"Removed {p}", verbose)
        else:
            log(f"Not found (skip): {p}", verbose)


# ---------- Commands ----------

def cmd_build(args):
    root = Path(args.path).resolve()
    collect_root = Path(args.collect).resolve()

    ensure_dir(collect_root / "Date", dry_run=args.dry_run, verbose=args.verbose)
    ensure_dir(collect_root / "Category", dry_run=args.dry_run, verbose=args.verbose)

    print(f"Scanning for collect files in {root}")
    count = 0
    for f in find_collect_files(root):
        d, cats = parse_collect_file(f, verbose=args.verbose)
        if not cats:
            continue
        index_entry(
            collect_root,
            f.parent.resolve(),
            d,
            cats,
            force=args.force,
            dry_run=args.dry_run,
            verbose=args.verbose,
            group_dates=args.group_dates,
        )
        count += 1
    print(f"Processed {count} collect file(s). Index at: {collect_root}")

def cmd_remove(args):
    collect_root = Path(args.collect).resolve()
    ensure_dir(collect_root, dry_run=args.dry_run, verbose=args.verbose)
    remove_indexes(collect_root, dry_run=args.dry_run, verbose=args.verbose)

def cmd_rebuild(args):
    # remove + build
    cmd_remove(args)
    cmd_build(args)

def cmd_hide(args):
    # macOS: simply rename visible txt/yaml to hidden equivalents
    root = Path(args.path).resolve()
    count = 0
    for f in find_collect_files(root):
        # Only hide if it's visible form
        if f.name.startswith("."):
            continue
        hidden = f.with_name("." + f.name)
        if args.dry_run:
            log(f"[dry-run] mv {f} {hidden}", args.verbose)
        else:
            f.rename(hidden)
            log(f"Renamed {f} -> {hidden}", args.verbose)
        count += 1
    print(f"Hid {count} file(s).")


# ---------- CLI ----------

def common_flags(ap):
    ap.add_argument("-p", "--path", default=".", help="Root to search for collect files.")
    ap.add_argument("-c", "--collect", default=str(Path.home() / "Documents" / "__Collect__"),
                    help="Path to __Collect__ index root.")
    ap.add_argument("-n", "--dry-run", action="store_true", help="Show actions without changing anything.")
    ap.add_argument("-f", "--force", action="store_true", help="Replace existing links/folders when rebuilding.")
    ap.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")
    ap.add_argument("--group-dates", action="store_true",
                    help="Use Date/YYYY/MM/DD instead of Date/YYYY-MM-DD.")

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Build a Date/Category symlink index from collect files (txt or YAML)."
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_build = sub.add_parser("build", help="Build or update the symlink index.")
    common_flags(ap_build)
    ap_build.set_defaults(func=cmd_build)

    ap_remove = sub.add_parser("remove", help="Remove Date/ and Category/ indexes.")
    common_flags(ap_remove)
    ap_remove.set_defaults(func=cmd_remove)

    ap_rebuild = sub.add_parser("rebuild", help="Remove and rebuild the indexes.")
    common_flags(ap_rebuild)
    ap_rebuild.set_defaults(func=cmd_rebuild)

    ap_hide = sub.add_parser("hide", help="Rename visible collect files to hidden (prefix with .).")
    # hide operates on the search root only; index flags not necessary but harmless
    common_flags(ap_hide)
    ap_hide.set_defaults(func=cmd_hide)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
