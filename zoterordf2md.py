import argparse
import glob
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


def convert_pdf_to_md(pdf_path, output_folder, method="auto"):
    """Convert a PDF file to a Markdown file using the magic-pdf application."""
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    md_folder = os.path.join(output_folder, base_name, method)
    md_name = os.path.join(md_folder, base_name + ".md")

    os.makedirs(md_folder, exist_ok=True)

    try:
        subprocess.run(['magic-pdf', '-p', pdf_path,
                        '-o', output_folder, '-m', method], check=True)
        print(f"Converted {pdf_path} to {md_name}")
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

    # cleanup tempary files
    post_fix_clean = ["_content_list.json", "_layout.pdf",
                      "_middle.json", "_model.json", "_origin.pdf", "_spans.pdf"]
    for pdf_path in pdf_paths:
        filename = os.path.basename(pdf_path)
        base_name = os.path.splitext(filename)[0]
        for pf in post_fix_clean:
            temp_file = os.path.join(
                args.output_folder, base_name, "auto", f"{base_name}{pf}")
            if os.path.exists(temp_file):
                print(f"Removing {temp_file}")
                os.remove(temp_file)


if __name__ == "__main__":
    main()
