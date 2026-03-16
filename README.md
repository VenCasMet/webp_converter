# 🖼️ Batch Image to WebP Converter

A **high-performance Python tool** to batch convert images into **WebP format** using **Pillow**.
The script supports **multi-threading, metadata handling, optional resizing, verification mode, archiving, logging, and detailed JSON reporting**.

It is designed to process **large image directories efficiently** while optionally preserving the original folder structure or flattening the output.

---

# 🚀 Features

## 1️⃣ Batch Image Conversion

Convert large collections of images into **WebP format** in a single run.

Supported input formats:

* PNG
* JPG / JPEG
* BMP
* TIFF / TIF
* GIF

---

## 2️⃣ Automatic Compression Mode

The script intelligently selects the compression mode based on the file format.

| Format              | Compression Mode |
| ------------------- | ---------------- |
| PNG, BMP, TIFF, GIF | Lossless         |
| JPG, JPEG           | Lossy            |

---

## 3️⃣ Multi-threaded Processing ⚡

Uses **ThreadPoolExecutor** to process multiple images simultaneously.

Default:

```
4 workers
```

You can customize using:

```
--workers
```

Example:

```
--workers 8
```

---

## 4️⃣ Image Verification Mode 🔍

Verify whether images are **valid or corrupted** without performing conversion.

Uses Pillow’s:

```
img.verify()
```

Activate with:

```
--verify-only
```

---

## 5️⃣ Metadata Handling 📊

During processing the script logs:

* image dimensions
* color mode
* file size

It also:

* removes **ICC profiles**
* converts colors to **sRGB**
* handles unusual color modes

---

## 6️⃣ Large Image Handling 🧠

If images exceed **100 million pixels**, they are automatically resized to prevent memory crashes.

---

## 7️⃣ Optional Image Resizing 📐

Resize images during conversion.

Example:

```
--max-size 1024
```

---

## 8️⃣ Automatic Archive of Original Images 📦

Before compression, the script creates a **backup archive of original images** to ensure data safety.

Structure:

```
compressed_images/
   └── archive/
```

---

## 9️⃣ Clean Output Filenames 🧹

The script automatically:

* removes spaces from filenames
* limits filenames to **30 characters**

This ensures compatibility across systems.

---

## 🔟 Logging System 📝

Execution logs are automatically generated and stored inside:

```
logs/
```

Example log:

```
logs/compression_1710000000.log
```

Logs include:

* processing information
* errors
* performance timing

---

## 1️⃣1️⃣ JSON Reporting 📄

Generate a **detailed JSON report** including:

* file name
* file type
* compression status
* size reduction
* resolution after compression
* errors if any

Example report entry:

```json
{
  "file_name": "photo.png",
  "file_type": ".png",
  "compression_status": true,
  "size_reduced_bytes": 102345,
  "resolution_after_compression": "1920x1080"
}
```

---

# 📦 Requirements

## Python

```
Python 3.8+
```

## Install Dependencies

```
pip install pillow
```

---

## Verify WebP Support

Run:

```python
from PIL import features
print(features.check("webp"))
```

Expected output:

```
True
```

---

# 📂 Project Structure

Example structure:

```
project/
│
├── convert_to_webp.py
├── README.md
│
├── images/
│   ├── img1.jpg
│   ├── img2.png
│   └── folder/
│       └── img3.tiff
│
├── compressed_images/
│   ├── archive/
│   └── converted .webp images
│
├── logs/
│   └── compression_1710000000.log
│
└── final_report.json
```

---

# ▶️ Basic Usage

Run the script using:

```
python convert_to_webp.py --input <input_folder>
```

Example:

```
python convert_to_webp.py --input images
```

Output will be created automatically:

```
images_webp_output/
```

---

# ⚙️ Command Line Options

| Argument        | Description                                 |
| --------------- | ------------------------------------------- |
| `--input`       | Input directory containing images           |
| `--output`      | Output directory                            |
| `--quality`     | WebP quality for lossy images (default: 85) |
| `--method`      | WebP compression effort (0–6)               |
| `--max-size`    | Resize images to max dimension              |
| `--overwrite`   | Overwrite existing output files             |
| `--flat`        | Do not preserve folder structure            |
| `--workers`     | Number of parallel threads                  |
| `--report`      | Save JSON report                            |
| `--verify-only` | Only check images for corruption            |

---

# 💻 Command Examples

## 1️⃣ Basic Conversion

Convert all images inside a folder.

```
python convert_to_webp.py --input images
```

---

## 2️⃣ Specify Output Directory

```
python convert_to_webp.py --input images --output converted_images
```

---

## 3️⃣ High Quality Conversion

```
python convert_to_webp.py --input images --quality 95
```

---

## 4️⃣ Faster Compression

Lower compression method = faster.

```
python convert_to_webp.py --input images --method 3
```

---

## 5️⃣ Resize Images

Resize large images during conversion.

```
python convert_to_webp.py --input images --max-size 1024
```

---

## 6️⃣ Use More Threads

Speed up conversion using multiple threads.

```
python convert_to_webp.py --input images --workers 8
```

---

## 7️⃣ Flatten Folder Structure

All output images will be stored in a single directory.

```
python convert_to_webp.py --input images --flat
```

---

## 8️⃣ Overwrite Existing Files

```
python convert_to_webp.py --input images --overwrite
```

---

## 9️⃣ Generate JSON Report

```
python convert_to_webp.py --input images --report report.json
```

Example report entry:

```json
{
  "src": "images/photo.jpg",
  "dst": "output/photo.webp",
  "success": true,
  "mode": "lossy",
  "src_size": 245678,
  "dst_size": 85632
}
```

---

## 🔟 Verify Images Only

Check for corrupted images.

```
python convert_to_webp.py --input images --verify-only
```

Example result:

```
valid image → success
corrupt image → error logged
```

---

# 🧪 Example Full Command

```
python convert_to_webp.py \
--input images \
--output webp_images \
--quality 90 \
--method 6 \
--workers 8 \
--max-size 2048 \
--report report.json
```

---

# ⚡ Performance Tips

Use more workers for SSD systems:

```
--workers 8
```

For fastest processing:

```
--method 3
```

For best compression:

```
--method 6
--quality 90
```

---

# 📝 Example Output Log

```
2026-03-12 12:00:01 | INFO | Found 120 images
2026-03-12 12:00:02 | INFO | Processing image1.jpg | 1920x1080 | RGB | 2.1 MB
2026-03-12 12:00:02 | INFO | Processing image2.png | 512x512 | RGBA | 450 KB
2026-03-12 12:00:05 | INFO | Processed 120 images in 3.20s
```

---

# 🛡️ Error Handling

The script gracefully handles:

* corrupted images
* oversized images
* memory issues
* unsupported formats

Errors are logged and included in the JSON report.

---

# 💻 Supported Platforms

* Windows
* Linux
* macOS

---

# 📜 License

This project can be used for **personal or commercial purposes**.
