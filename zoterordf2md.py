import argparse
import re
import subprocess
import os


def extract_pdf_paths(rdf_file):
    """Extract PDF paths from an RDF file."""
    pdf_paths = []
    with open(rdf_file, 'r') as file:
        content = file.read()
        # Use regex to find all occurrences of rdf:resource="files/**.pdf"
        matches = re.findall(r'rdf:resource="(files/[^"]+\.pdf)"', content)
        pdf_paths.extend(matches)
    return pdf_paths


def convert_pdf_to_md(pdf_path, output_folder):
    """Convert a PDF file to a Markdown file using the magic-pdf application."""
    md_filename = os.path.basename(os.path.splitext(pdf_path)[0] + '.md')
    md_path = os.path.join(output_folder, md_filename)
    try:
        subprocess.run(['magic-pdf', '-p', pdf_path,
                       '-o', md_path], check=True)
        print(f"Converted {pdf_path} to {md_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {pdf_path} to Markdown. Error: {e}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract PDF paths from an RDF file and convert them to Markdown.")
    parser.add_argument("rdf_file_path", type=str,
                        help="Path to the RDF file to process.")
    parser.add_argument("--output_folder", type=str, default="results",
                        help="Folder to save the Markdown files.")
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Extract PDF paths
    pdf_paths = extract_pdf_paths(args.rdf_file_path)
    print("PDF paths found:", pdf_paths)

    # Convert each PDF to Markdown
    for pdf_path in pdf_paths:
        convert_pdf_to_md(pdf_path, args.output_folder)


if __name__ == "__main__":
    main()
