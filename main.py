import sys
import argparse
from pathlib import Path

# Add the 'src' directory to the Python path so it can find our modules
# This allows us to keep the root directory clean!
sys.path.append(str(Path(__file__).parent / "src"))

from config_parser import parse_config
from file_walker import get_files_to_process
from compiler import compile_project_snapshot

def main():
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Generate a single-file markdown summary of your code project."
    )
    parser.add_argument(
        "config", 
        help="Path to the input TOML configuration file (e.g., myproject.toml)"
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    
    # 1. Validate input file
    if not config_path.is_file():
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)

    # The stem is the filename without the extension (e.g., "myproject")
    project_name = config_path.stem
    output_path = config_path.with_suffix(".md")

    print(f"🔍 Parsing configuration from '{config_path}'...")
    try:
        config = parse_config(config_path)
    except Exception as e:
        print(f"Error parsing TOML file: {e}")
        sys.exit(1)

    print("📂 Discovering and filtering files...")
    target_files = get_files_to_process(config)
    print(f"✅ Found {len(target_files)} files to process.")

    if not target_files:
        print("⚠️ No files matched your configuration rules. Exiting.")
        sys.exit(0)

    print("⚙️  Compiling code snapshot (collapsing functions if configured)...")
    tree_string, markdown_body = compile_project_snapshot(target_files)

    # 2. Add the required header and the new directory tree
    final_document = (
        f"# Code Snapshot for `{project_name}`\n\n"
        f"## Project Structure\n\n{tree_string}\n\n"
        f"---\n\n"
        f"{markdown_body}"
    )

    # 3. Write to the output file
    print(f"📝 Writing output to '{output_path}'...")
    try:
        output_path.write_text(final_document, encoding="utf-8")
        print("🎉 Success! Your code summary is ready.")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()