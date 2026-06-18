from flask import Flask, render_template, request, jsonify
import os
import shutil
import re
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

app = Flask(__name__)

# ===== Configuration =====
if os.environ.get("VERCEL"):
    UPLOAD_FOLDER = '/tmp/uploads'
    OUTPUT_FOLDER = '/tmp/output'
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


# ===== Task 1: Move .jpg files =====
@app.route("/api/move-images", methods=["POST"])
def move_images():
    """Move all .jpg files from source folder to a new destination folder."""
    data = request.get_json()
    source_dir = data.get("source_dir", "").strip()

    if not source_dir:
        return jsonify({"success": False, "message": "Please provide a source directory path."})

    if not os.path.isdir(source_dir):
        return jsonify({"success": False, "message": f"Directory not found: {source_dir}"})

    # Create destination folder
    dest_dir = os.path.join(source_dir, "jpg_files")
    os.makedirs(dest_dir, exist_ok=True)

    moved_files = []
    skipped_files = []

    for filename in os.listdir(source_dir):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(dest_dir, filename)

            if os.path.isfile(src_path):
                try:
                    shutil.move(src_path, dst_path)
                    moved_files.append(filename)
                except Exception as e:
                    skipped_files.append({"file": filename, "error": str(e)})

    if not moved_files and not skipped_files:
        return jsonify({
            "success": True,
            "message": "No .jpg files found in the specified directory.",
            "moved": [],
            "skipped": [],
            "destination": dest_dir
        })

    return jsonify({
        "success": True,
        "message": f"Successfully moved {len(moved_files)} file(s) to {dest_dir}",
        "moved": moved_files,
        "skipped": skipped_files,
        "destination": dest_dir
    })


# ===== Task 2: Extract emails from .txt file =====
@app.route("/api/extract-emails", methods=["POST"])
def extract_emails():
    """Extract all email addresses from uploaded text content or a .txt file path."""
    data = request.get_json()
    text_content = data.get("text_content", "").strip()
    file_path = data.get("file_path", "").strip()

    if file_path:
        if not os.path.isfile(file_path):
            return jsonify({"success": False, "message": f"File not found: {file_path}"})
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        except Exception as e:
            return jsonify({"success": False, "message": f"Error reading file: {str(e)}"})

    if not text_content:
        return jsonify({"success": False, "message": "Please provide text content or a file path."})

    # Regex pattern for email extraction
    email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, text_content)))
    emails.sort()

    # Save extracted emails to output file
    output_file = os.path.join(OUTPUT_FOLDER, f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(output_file, 'w') as f:
        f.write(f"# Extracted Emails - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total: {len(emails)} unique email(s) found\n\n")
        for email in emails:
            f.write(email + "\n")

    return jsonify({
        "success": True,
        "message": f"Found {len(emails)} unique email(s).",
        "emails": emails,
        "total": len(emails),
        "saved_to": output_file
    })


# ===== Task 3: Scrape webpage title =====
@app.route("/api/scrape-title", methods=["POST"])
def scrape_title():
    """Scrape the title of a given webpage URL."""
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "message": "Please provide a URL."})

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"

        # Also grab meta description if available
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content'].strip()

        # Save result
        output_file = os.path.join(OUTPUT_FOLDER, f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n")
            f.write(f"Title: {title}\n")
            f.write(f"Description: {meta_desc}\n")
            f.write(f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        return jsonify({
            "success": True,
            "message": "Successfully scraped the webpage!",
            "url": url,
            "title": title,
            "description": meta_desc,
            "saved_to": output_file
        })

    except requests.exceptions.Timeout:
        return jsonify({"success": False, "message": "Request timed out. Please try again."})
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "message": "Could not connect to the URL. Please check the address."})
    except requests.exceptions.HTTPError as e:
        return jsonify({"success": False, "message": f"HTTP Error: {str(e)}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


# ===== History / Stats =====
@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get stats about output files generated."""
    output_files = []
    if os.path.isdir(OUTPUT_FOLDER):
        for f in os.listdir(OUTPUT_FOLDER):
            filepath = os.path.join(OUTPUT_FOLDER, f)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                output_files.append({
                    "name": f,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })

    return jsonify({
        "success": True,
        "output_folder": OUTPUT_FOLDER,
        "files": sorted(output_files, key=lambda x: x["created"], reverse=True),
        "total_files": len(output_files)
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
