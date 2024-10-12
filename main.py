r'''
Activate venv: .\venv\Scripts\activate

'''




import os
import re
import shutil
import markdown


INPUT_FOLDER = 'files'
OUTPUT_FOLDER = 'output'


def convert_md_links_to_html(content):
    # Regex to find markdown links of the form [text](file.md)
    md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\.md\)'
    # Replace with the equivalent HTML link [text](file.html)
    return re.sub(md_link_pattern, r'[\1](\2.html)', content)




def process_markdown_file(md_file_path, output_file_path):
    # Read the markdown content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown links to HTML links
    md_content = convert_md_links_to_html(md_content)


    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    # Replace code blocks with <pre><code> with optional language class
    def code_block_replacement(match):
        language = match.group(1) or ''  # e.g., python
        code_content = match.group(2)    # the code inside the block
        # Escape HTML characters in the code block content
        code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if language:
            return f'<pre><code class="language-{language}">{code_content}</code></pre>'
        else:
            return f'<pre><code>{code_content}</code></pre>'

    code_content = re.sub(code_block_pattern, code_block_replacement, md_content, flags=re.DOTALL)

    


    # Convert markdown to HTML
    html_content = markdown.markdown(code_content)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)



def handle_file_conversion(input_path, output_path):
    if input_path.endswith('.md'):
        output_file_path = output_path.replace('.md', '.html')
        process_markdown_file(input_path, output_file_path)
    else:
        shutil.copy2(input_path, output_path)



def process_folder(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        target_folder = os.path.join(output_folder, relative_path)

        os.makedirs(target_folder, exist_ok=True)

        for file in files:
            input_file_path = os.path.join(root, file)
            output_file_path = os.path.join(target_folder, file)
            
            handle_file_conversion(input_file_path, output_file_path)



def run_ssg(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)


    process_folder(input_folder, output_folder)


run_ssg()
