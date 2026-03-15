# Batch Image to WebP Converter

A high-performance Python tool to batch convert images into WebP format using Pillow with multi-threading, metadata handling, optional resizing, verification mode, and detailed JSON reporting.
This tool supports converting large directories of images efficiently while maintaining directory structure or flattening output if desired.

## Features

### 1. Batch Image Conversion

Convert large collections of images to WebP format in a single run.

Supported input formats:

-PNG

-JPG / JPEG

-BMP

-TIFF / TIF

-GIF

### 2. Automatic Compression Mode

The script intelligently chooses the compression type:

Format	Compression
    
    PNG, BMP, TIFF, GIF---------Lossless
    JPG, JPEG-------------------Lossy

### 3. Multi-threaded Processing

Uses ThreadPoolExecutor to process multiple images simultaneously.

Default workers:

4 threads

You can customize this using --workers.

### 4. Image Verification Mode

Check if images are corrupted or invalid without converting them.

Uses Pillow's img.verify() method.

### 5. Metadata Handling

The script logs:

-image dimensions

-color mode

-file size

It also:

-removes ICC profiles

-converts colors to sRGB

-handles unusual color modes

### 6. Large Image Handling

If images exceed 100 million pixels, they are automatically resized to avoid memory crashes.

### 7. Optional Image Resizing

Resize images during conversion using:

    --max-size

Example:

    --max-size 1024

### 8. JSON Reporting

Generate a detailed JSON report including:

-source file

-destination file

-compression mode

-original size

-converted size

-errors

skipped files

### 9. Robust Error Handling

-Handles common errors:

-MemoryError

-OSError

-DecompressionBombError

-Corrupted images

## Requirements

Python

    Python 3.8 or newer

Install dependencies

     pip install pillow

Verify WebP Support

Run:

    from PIL import features
    print(features.check("webp"))

Expected output:

True

## Project Structure

Example structure:

    project/
    │
    ├── convert_to_webp.py
    ├── README.md
    │
    └── images/
        ├── img1.jpg
        ├── img2.png
        └── folder/
            └── img3.tiff
        
## Basic Usage

Run the script using:

    python convert_to_webp.py --input <input_folder>

Example:

    python convert_to_webp.py --input images

Output will be created automatically:

    images_webp_output/

## Command Line Options

    Argument	       Description
    --input	         Input directory containing images
    --output	       Output directory
    --quality	       WebP quality for lossy images (default: 85)
    --method	       WebP compression effort (0–6)
    --max-size	     Resize images to max dimension
    --overwrite	     Overwrite existing output files
    --flat	         Do not preserve folder structure
    --workers	       Number of parallel threads
    --report	       Save JSON report
    --verify-only	   Only check images for corruption

## Command Examples

### 1. Basic Conversion

Convert all images inside a folder.

    python convert_to_webp.py --input images

### 2. Specify Output Directory

    python convert_to_webp.py --input images --output converted_images

### 3. High Quality Conversion

    python convert_to_webp.py --input images --quality 95

### 4. Faster Compression

Lower compression method = faster.

    python convert_to_webp.py --input images --method 3

### 5. Resize Images

Resize large images during conversion.

    python convert_to_webp.py --input images --max-size 1024

### 6. Use More Threads

Speed up conversion using multiple threads.

    python convert_to_webp.py --input images --workers 8

### 7. Flatten Folder Structure

All output images will be stored in a single directory.

    python convert_to_webp.py --input images --flat

### 8. Overwrite Existing Files

    python convert_to_webp.py --input images --overwrite

### 9. Generate JSON Report

    python convert_to_webp.py --input images --report report.json

Example report entry:

    {
      "src": "images/photo.jpg",
      "dst": "output/photo.webp",
      "success": true,
      "mode": "lossy",
      "src_size": 245678,
      "dst_size": 85632
    }

### 10. Verify Images Only

Check for corrupted images.

    python convert_to_webp.py --input images --verify-only

Example result:

    valid image -> success
    corrupt image -> error logged

Example Full Command

    python convert_to_webp.py \
    --input images \
    --output webp_images \
    --quality 90 \
    --method 6 \
    --workers 8 \
    --max-size 2048 \
    --report report.json

## Performance Tips

Use more workers for SSD systems
    
    --workers 8

For fastest processing

    --method 3

For best compression

    --method 6
    --quality 90

Example Output Log

    2026-03-12 12:00:01 | INFO | Found 120 images
    2026-03-12 12:00:02 | INFO | Processing image1.jpg | 1920x1080 | RGB | 2.1 MB
    2026-03-12 12:00:02 | INFO | Processing image2.png | 512x512 | RGBA | 450 KB
    2026-03-12 12:00:05 | INFO | Processed 120 images in 3.20s

## Error Handling

-The script gracefully handles:

-corrupted images

-oversized images

-memory issues

-unsupported formats

Errors are logged and included in the JSON report.

## Supported Platforms

-Windows

-Linux

-macOS

## License

This project can be used for personal or commercial purposes.
