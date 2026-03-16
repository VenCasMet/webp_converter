import os
import sys
import time
import json
import argparse
import logging
import shutil
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageFile, ImageCms, features

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

SUPPORTED = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif"}

LOSSLESS_FORMATS = {".png", ".bmp", ".tiff", ".tif", ".gif"}
LOSSY_FORMATS = {".jpg", ".jpeg"}

# ───────────── Logging Setup ─────────────

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"compression_{int(time.time())}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ───────────── Utilities ─────────────

def human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


def clean_filename(name: str) -> str:
    name = name.replace(" ", "_")
    return name[:30]


def collect_images(root: Path) -> List[Path]:

    images = []

    for dirpath, _, filenames in os.walk(root):

        for fn in filenames:

            if Path(fn).suffix.lower() in SUPPORTED:
                images.append(Path(dirpath) / fn)

    return sorted(images)


def output_path(src: Path, input_root: Path, output_root: Path) -> Path:

    rel = src.relative_to(input_root)

    clean_name = clean_filename(src.stem)

    return output_root / rel.parent / (clean_name + ".webp")


def get_compression_mode(src: Path):

    ext = src.suffix.lower()

    if ext in LOSSY_FORMATS:
        return False, "lossy"

    return True, "lossless"


# ───────────── Archive Original Images ─────────────

def archive_images(images: List[Path], archive_dir: Path):

    archive_dir.mkdir(parents=True, exist_ok=True)

    for img in images:

        try:
            shutil.copy2(img, archive_dir / img.name)

        except Exception as e:
            logger.warning(f"Archive failed for {img}: {e}")


# ───────────── Image Conversion ─────────────

def convert_image(
        src: Path,
        dst: Path,
        quality: int,
        method: int,
        overwrite: bool
) -> Dict:

    lossless, mode_label = get_compression_mode(src)

    result = {
        "file_name": src.name,
        "file_type": src.suffix,
        "compression_status": False,
        "src_size": src.stat().st_size,
        "dst_size": 0,
        "size_reduced": 0,
        "resolution_after": None,
        "error": None
    }

    if dst.exists() and not overwrite:
        return result

    try:

        dst.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(src) as img:

            logger.info(
                f"Processing {src.name} | "
                f"{img.width}x{img.height} | "
                f"{human_size(src.stat().st_size)}"
            )

            # Color conversion
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Convert ICC profile
            try:
                if "icc_profile" in img.info:

                    srgb = ImageCms.createProfile("sRGB")

                    img = ImageCms.profileToProfile(
                        img,
                        img.info.get("icc_profile"),
                        srgb
                    )

            except Exception:
                pass

            img.info.pop("icc_profile", None)

            save_kwargs = {
                "format": "WEBP",
                "lossless": lossless,
                "method": method
            }

            if not lossless:
                save_kwargs["quality"] = quality

            img.save(dst, **save_kwargs)

        result["dst_size"] = dst.stat().st_size
        result["size_reduced"] = result["src_size"] - result["dst_size"]
        result["compression_status"] = True

        with Image.open(dst) as im:
            result["resolution_after"] = f"{im.width}x{im.height}"

    except Exception as e:

        result["error"] = str(e)

    return result


# ───────────── Runner ─────────────

def run_conversion(
        images: List[Path],
        input_root: Path,
        output_root: Path,
        quality: int,
        method: int,
        overwrite: bool,
        workers: int
):

    results = []

    start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = []

        for src in images:

            dst = output_path(src, input_root, output_root)

            futures.append(
                executor.submit(
                    convert_image,
                    src,
                    dst,
                    quality,
                    method,
                    overwrite
                )
            )

        for future in as_completed(futures):

            results.append(future.result())

    elapsed = time.time() - start

    logger.info(f"Processed {len(images)} images in {elapsed:.2f}s")

    return results


# ───────────── Generate Final Report ─────────────

def generate_report(results: List[Dict], report_path: Path):

    report = []

    for r in results:

        report.append({
            "file_name": r["file_name"],
            "file_type": r["file_type"],
            "compression_status": r["compression_status"],
            "size_reduced_bytes": r["size_reduced"],
            "resolution_after_compression": r["resolution_after"]
        })

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Final report saved to {report_path}")


# ───────────── CLI Arguments ─────────────

def parse_args():

    parser = argparse.ArgumentParser(
        description="Batch Image Compression Tool"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="compressed_images")

    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--method", type=int, default=6)

    parser.add_argument("--workers", type=int, default=4)

    parser.add_argument("--overwrite", action="store_true")

    return parser.parse_args()


# ───────────── Main ─────────────

def main():

    if not features.check("webp"):

        logger.error("Pillow installation does not support WebP")

        sys.exit(1)

    args = parse_args()

    input_root = Path(args.input).resolve()

    if not input_root.exists():

        logger.error("Input path does not exist")

        sys.exit(1)

    output_root = Path(args.output).resolve()

    images = collect_images(input_root)

    if not images:

        logger.warning("No images found")

        return

    logger.info(f"Found {len(images)} images")

    # Archive originals
    archive_dir = output_root / "archive"

    archive_images(images, archive_dir)

    logger.info("Original images archived")

    # Convert images
    results = run_conversion(
        images,
        input_root,
        output_root,
        args.quality,
        args.method,
        args.overwrite,
        args.workers
    )

    # Generate final report
    report_path = Path("final_report.json")

    generate_report(results, report_path)


if __name__ == "__main__":
    main()