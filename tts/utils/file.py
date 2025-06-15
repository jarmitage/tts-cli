import markdown
from bs4 import BeautifulSoup
import re
from pathlib import Path
from typing import Optional

def read_text_file(file_path: str) -> str:
    """Read text from a plain text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_markdown_file(file_path: str) -> str:
    """
    Read and convert markdown file to plain text.
    Strips HTML tags and handles basic markdown formatting.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html = markdown.markdown(md_content)
    
    # Parse HTML and extract text
    soup = BeautifulSoup(html, 'html.parser')
    
    # Handle headers and paragraphs with newlines
    for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        elem.append('\n\n')
    
    # Extract text and clean up whitespace
    text = soup.get_text()
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def read_input_file(input_file: str) -> str:
    """Read and process input file based on its type."""
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if input_path.suffix.lower() == '.md':
        return read_markdown_file(input_file)
    elif input_path.suffix.lower() == '.txt':
        return read_text_file(input_file)
    else:
        raise ValueError("Input file must be .txt or .md format")

def prepare_output_directory(output_path: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_path.mkdir(parents=True, exist_ok=True) 