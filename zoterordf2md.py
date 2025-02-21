import argparse
import re
import subprocess
import os


def extract_file_paths(rdf_file):
    """Extract file paths from an RDF file."""
    file_paths = []
    with open(rdf_file, 'r', encoding='utf-8') as file:
        content = file.read()
        # Use regex to find all occurrences of rdf:resource="files/**.{pdf,ppt,pptx,doc,docx}"
        matches = re.findall(
            r'rdf:resource="(files/[^"]+\.(pdf|ppt|pptx|doc|docx))"', content)
        file_paths.extend(match[0] for match in matches)
    return file_paths


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


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract file paths from an RDF file and convert them to Markdown.")
    parser.add_argument("rdf_file_path", type=str,
                        help="Path to the RDF file to process.")
    parser.add_argument("--method", type=str, default="auto",
                        help="Method to use for conversion.")
    parser.add_argument("--tmp_folder", type=str, default="tmp",
                        help="Folder to save temporary files.")
    parser.add_argument("--output_folder", type=str, default="results",
                        help="Folder to save the Markdown files.")
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)
    os.makedirs(args.tmp_folder, exist_ok=True)

    # Extract file paths
    file_paths = extract_file_paths(args.rdf_file_path)
    print("File paths found:", file_paths)

    # Convert each file to Markdown
    for file_path in file_paths:
        convert_file_to_md(file_path, args.tmp_folder, args.method)
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        md_file = os.path.join(args.tmp_folder, base_name,
                               args.method, f"{base_name}.md")
        if os.path.exists(md_file):
            print(f"Moving {md_file} to {args.output_folder}")
            os.rename(md_file, os.path.join(
                args.output_folder, f"{base_name}.md"))
        else:
            print(f"Markdown file {md_file} not found. Skipping.")


if __name__ == "__main__":
    main()
