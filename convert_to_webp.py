import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageFile, ImageCms, features

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

SUPPORTED = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif"}

LOSSLESS_FORMATS = {".png", ".bmp", ".tiff", ".tif", ".gif"}
LOSSY_FORMATS = {".jpg", ".jpeg"}

Image.MAX_IMAGE_PIXELS = None


# ───────────── Logging ─────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ───────────── Utilities ─────────────
def human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


def collect_images(root: Path) -> List[Path]:
    images = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if Path(fn).suffix.lower() in SUPPORTED:
                images.append(Path(dirpath) / fn)
    return sorted(images)


def output_path(src: Path, input_root: Path, output_root: Path, flat: bool) -> Path:
    if flat:
        return output_root / (src.stem + ".webp")

    rel = src.relative_to(input_root)
    return output_root / rel.parent / (src.stem + ".webp")


def get_compression_mode(src: Path):
    ext = src.suffix.lower()
    if ext in LOSSY_FORMATS:
        return False, "lossy"
    return True, "lossless"


# ───────────── Verify Image ─────────────
def verify_image(src: Path) -> Dict:

    result = {
        "src": str(src),
        "valid": False,
        "error": None
    }

    try:
        with Image.open(src) as img:
            img.verify()

        result["valid"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


# ───────────── Image Conversion ─────────────
def convert_image(
        src: Path,
        dst: Path,
        quality: int,
        method: int,
        overwrite: bool,
        max_size: int = None,
) -> Dict:

    lossless, mode_label = get_compression_mode(src)

    result = {
        "src": str(src),
        "dst": str(dst),
        "success": False,
        "skipped": False,
        "mode": mode_label,
        "src_size": src.stat().st_size,
        "dst_size": 0,
        "error": None
    }

    if dst.exists() and not overwrite:
        result["skipped"] = True
        result["dst_size"] = dst.stat().st_size
        return result

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(src) as img:

            # ── METADATA LOGGING ──
            logger.info(
                f"Processing {src.name} | "
                f"{img.width}x{img.height} | "
                f"{img.mode} | "
                f"{human_size(src.stat().st_size)}"
            )

            MAX_PIXELS = 100_000_000
            if img.width * img.height > MAX_PIXELS:
                logger.warning(f"Large image detected: {src.name}")
                img.thumbnail((8000, 8000), Image.LANCZOS)

            # Color mode conversion
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # ICC → sRGB conversion
            try:
                if "icc_profile" in img.info:
                    srgb_profile = ImageCms.createProfile("sRGB")
                    img = ImageCms.profileToProfile(
                        img,
                        img.info.get("icc_profile"),
                        srgb_profile
                    )
            except Exception:
                pass

            img.info.pop("icc_profile", None)

            # Resize if required
            if max_size:
                img.thumbnail((max_size, max_size), Image.LANCZOS)

            save_kwargs = {
                "format": "WEBP",
                "lossless": lossless,
                "method": method
            }

            if not lossless:
                save_kwargs["quality"] = quality

            img.save(dst, **save_kwargs)

        result["dst_size"] = dst.stat().st_size
        result["success"] = True

    except MemoryError:
        result["error"] = "MemoryError: image too large"

    except OSError as e:
        result["error"] = f"OSError: {e}"

    except Image.DecompressionBombError as e:
        result["error"] = f"DecompressionBombError: {e}"

    except ValueError as e:
        result["error"] = f"ValueError: {e}"

    return result


# ───────────── Runner ─────────────
def run_conversion(
        images: List[Path],
        input_root: Path,
        output_root: Path,
        quality: int,
        method: int,
        overwrite: bool,
        flat: bool,
        max_size: int,
        workers: int,
        verify_only: bool
):

    start = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = []

        for src in images:

            if verify_only:
                futures.append(executor.submit(verify_image, src))

            else:
                dst = output_path(src, input_root, output_root, flat)

                futures.append(
                    executor.submit(
                        convert_image,
                        src,
                        dst,
                        quality,
                        method,
                        overwrite,
                        max_size
                    )
                )

        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.time() - start

    logger.info(f"Processed {len(images)} images in {elapsed:.2f}s")

    return results


# ───────────── CLI ─────────────
def parse_args():

    p = argparse.ArgumentParser(
        description="Batch convert images to WebP"
    )

    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)

    p.add_argument("--quality", type=int, default=85)
    p.add_argument("--method", type=int, default=6)

    p.add_argument("--max-size", type=int, default=None)

    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--flat", action="store_true")

    p.add_argument("--workers", type=int, default=4)

    p.add_argument("--report", help="Save JSON report")

    # NEW FEATURE
    p.add_argument("--verify-only", action="store_true")

    return p.parse_args()


# ───────────── Main ─────────────
def main():

    if not features.check("webp"):
        logger.error("Your Pillow installation does not support WebP.")
        sys.exit(1)

    args = parse_args()

    input_root = Path(args.input).resolve()

    if not input_root.exists():
        logger.error(f"Input path does not exist: {input_root}")
        sys.exit(1)

    if args.output:
        output_root = Path(args.output).resolve()
    else:
        output_root = input_root.parent / (input_root.name + "_webp_output")

    images = collect_images(input_root)

    if not images:
        logger.warning("No supported images found.")
        return

    logger.info(f"Found {len(images)} images")

    results = run_conversion(
        images,
        input_root,
        output_root,
        args.quality,
        args.method,
        args.overwrite,
        args.flat,
        args.max_size,
        args.workers,
        args.verify_only
    )

    if args.report:
        with open(args.report, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Report saved to {args.report}")


if __name__ == "__main__":
    main()