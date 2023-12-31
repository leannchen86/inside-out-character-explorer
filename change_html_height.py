import os

def update_html_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                if '#mynetwork {' in content:
                    content = content.replace('height: 800px;', 'height: 350px;')
            
            with open(os.path.join(directory, filename), 'w', encoding='utf-8') as file:
                file.write(content)

# Update all HTML files in the specified directory
update_html_files('scenes/')
