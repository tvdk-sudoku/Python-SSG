r'''
Activate venv: .\venv\Scripts\activate


TODO:
- Add syntax highlighting to code blocks
- Add a CSS file to style the HTML output
- Add a table of contents to the HTML output
- Add a navigation bar to the HTML output
- Add a footer to the HTML output
- Add a title to the HTML output






'''



import os
import re
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader

INPUT_FOLDER = 'files'
OUTPUT_FOLDER = 'output'
TEMPLATE_FOLDER = 'templates'
SCRIPT_FOLDER = 'scripts'  # For CSS/JS files

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))

# Function to convert markdown links to html links
def convert_md_links_to_html(content):
    md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\.md\)'
    return re.sub(md_link_pattern, r'[\1](\2.html)', content)

# Function to parse frontmatter (metadata)
def parse_frontmatter(content):
    frontmatter_pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    if match:
        metadata = match.group(1)
        markdown_content = match.group(2)
        return metadata, markdown_content
    return None, content

# Function to extract template name from metadata
def extract_template(metadata):
    if metadata:
        template_pattern = r'template:\s*[\'"]([^\'"]+)[\'"]'
        match = re.search(template_pattern, metadata)
        if match:
            return match.group(1)
    return 'default'  # Default template if none specified

# Function to extract title from metadata
def extract_title(metadata):
    if metadata:
        title_pattern = r'title:\s*[\'"]([^\'"]+)[\'"]'
        match = re.search(title_pattern, metadata)
        if match:
            return match.group(1)
    return ''  # Default title if none specified

# Function to check if the file is marked as draft
def is_draft(metadata):
    draft_pattern = r'draft:\s*true'
    return metadata and re.search(draft_pattern, metadata, re.IGNORECASE)

# Function to generate Table of Contents (ToC) and modify headings to add anchor links
def generate_toc(content):
    toc = []
    heading_pattern = re.compile(r'^(#{1,6})\s*(.*)', re.MULTILINE)
    anchor_id = 0

    def heading_replacement(match):
        nonlocal anchor_id
        heading_level = len(match.group(1))  # Number of # symbols
        heading_text = match.group(2).strip()  # Heading text
        anchor_name = f'heading-{anchor_id}'  # Generate a unique anchor ID
        anchor_id += 1
        # Add to the ToC list with proper indentation
        toc.append((heading_level, heading_text, anchor_name))
        # Return the modified heading with the anchor link
        return f'<h{heading_level} id="{anchor_name}">{heading_text}</h{heading_level}>'

    # Replace headings in content and generate ToC
    modified_content = re.sub(heading_pattern, heading_replacement, content)

    # Create ToC HTML
    toc_html = '<div class="toc">\n<ol>\n'
    current_level = 1
    for level, text, anchor in toc:
        if level > current_level:
            toc_html += '<ol>\n' * (level - current_level)
        elif level < current_level:
            toc_html += '</ol>\n' * (current_level - level)
        toc_html += f'<li><a href="#{anchor}">{text}</a></li>\n'
        current_level = level
    toc_html += '</ol>\n</div>\n'

    return toc_html, modified_content

# Function to load the HTML template
def load_template(template_name):
    try:
        return env.get_template(f"{template_name}.html")
    except Exception as e:
        print(f"Error loading template {template_name}.html: {e}")
        return env.get_template("default.html")

# Function to process a markdown file
def process_markdown_file(md_file_path, output_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Parse frontmatter metadata and markdown content
    metadata, markdown_content = parse_frontmatter(md_content)

    # Extract the title from the metadata
    title = extract_title(metadata)

    # Check if the file is a draft
    if is_draft(metadata):
        html_content = "<h1>This page is a draft</h1><p>This content is currently unavailable.</p>"
        toc_html = ''
    else:
        # Convert markdown links to HTML links
        markdown_content = convert_md_links_to_html(markdown_content)

        # Convert code blocks and other markdown to HTML
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        def code_block_replacement(match):
            language = match.group(1) or ''
            code_content = match.group(2).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if language:
                return f'<pre><code class="language-{language}">{code_content}</code></pre>'
            else:
                return f'<pre><code>{code_content}</code></pre>'
        markdown_content = re.sub(code_block_pattern, code_block_replacement, markdown_content, flags=re.DOTALL)

        # Generate ToC and modified content with anchor links
        toc_html, markdown_content = generate_toc(markdown_content)

        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)

    # Extract the template name from the metadata
    template_name = extract_template(metadata)

    # Load the corresponding HTML template
    template = load_template(template_name)

    # Render the final HTML with the template, inserting the HTML content, ToC, and title
    final_html = template.render(content=html_content, toc=toc_html, title=title, scripts_folder=SCRIPT_FOLDER)

    # Write the final HTML to the output file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

# Function to handle file conversion or copying for non-markdown files
def handle_file_conversion(input_path, output_path):
    if input_path.endswith('.md'):
        output_file_path = output_path.replace('.md', '.html')
        process_markdown_file(input_path, output_file_path)
    else:
        shutil.copy2(input_path, output_path)

# Function to recursively process the input folder
def process_folder(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        target_folder = os.path.join(output_folder, relative_path)

        os.makedirs(target_folder, exist_ok=True)

        for file in files:
            input_file_path = os.path.join(root, file)
            output_file_path = os.path.join(target_folder, file)
            handle_file_conversion(input_file_path, output_file_path)

# Main function to run the SSG
def run_ssg(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    process_folder(input_folder, output_folder)

# Uncomment below line to run the script in a local environment
run_ssg()
