import argparse
import re
import subprocess
import os


def scan_pdf_files(folder_path):
    """Scan a folder for PDF files and return their paths."""
    pdf_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


def convert_file_to_md(file_path, tmp_folder, method="auto"):
    """Convert a file to a Markdown file using the magic-pdf application."""
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0]
    md_folder = os.path.join(tmp_folder, base_name, method)
    md_name = os.path.join(md_folder, base_name + ".md")

    os.makedirs(md_folder, exist_ok=True)

    try:
        subprocess.run(['magic-pdf', '-p', file_path,
                        '-o', tmp_folder, '-m', method], check=True)
        print(f"Converted {file_path} to {md_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {file_path} to Markdown. Error: {e}")


def parse_folder_names(path):
    """Parse and return the folder names of each layer in a given path."""
    folder_names = []
    while True:
        path, folder = os.path.split(path)
        if folder:
            # Add folder to the beginning of the list
            folder_names.insert(0, folder)
        else:
            if path:  # Add the root directory if it exists
                folder_names.insert(0, path)
            break
    return folder_names


def subtract_folder_names(folder_names1, folder_names2):
    """
    Calculate the subtraction of two lists of folder names.
    Returns the elements in folder_names2 that are not in folder_names1.
    """
    if folder_names1[:len(folder_names2)] == folder_names2:
        return folder_names1[len(folder_names2):]
    else:
        raise ValueError("folder_names2 is not a prefix of folder_names1")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract file paths from an RDF file and convert them to Markdown.")
    parser.add_argument("folder_path", type=str, default="ZoteroPDF",
                        help="Path to the folder to scan.")
    parser.add_argument("--method", type=str, default="auto",
                        help="Method to use for conversion.")
    parser.add_argument("--tmp_folder", type=str, default="tmp",
                        help="Folder to save temporary files.")
    parser.add_argument("--output_folder", type=str, default="ZoteroMD",
                        help="Folder to save the Markdown files.")
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)
    os.makedirs(args.tmp_folder, exist_ok=True)

    # Scan for PDF files
    pdf_files = scan_pdf_files(args.folder_path)

    # Convert each file to Markdown
    for file_path in pdf_files:
        # Check whether the pdf has already been converted
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        folder_names = subtract_folder_names(
            parse_folder_names(os.path.dirname(file_path)), parse_folder_names(args.folder_path))
        target_folder = os.path.join(args.output_folder, *folder_names)
        os.makedirs(target_folder, exist_ok=True)
        md_filename = os.path.join(
            args.output_folder, *folder_names, f"{base_name}.md")
        if not os.path.exists(md_filename):
            print(f"Converting {file_path} to Markdown.")
            convert_file_to_md(file_path, args.tmp_folder, args.method)
            tmp_md_file = os.path.join(
                args.tmp_folder, base_name, args.method, f"{base_name}.md")
            print(f"Moving {tmp_md_file} to {md_filename}")
            os.rename(tmp_md_file, md_filename)
        else:
            print(f"Markdown file {md_filename} already exists. Skipping.")


if __name__ == "__main__":
    main()
