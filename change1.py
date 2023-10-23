import os
import re

def update_html_files(directory, translation_value='-10%'):
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

                # Search for the #mynetwork style
                start_idx = content.find("#mynetwork {")
                if start_idx != -1:
                    end_idx = content.find("}", start_idx)
                    original_style = content[start_idx:end_idx+1]

                    # Remove any existing transform: translateY property
                    original_style_clean = re.sub(r'transform: translateY\([-0-9%]*\);', '', original_style)
                    
                    # Append the new transform property
                    new_style = original_style_clean.replace('position: relative;', f'position: relative; transform: translateY({translation_value});')
                    content = content.replace(original_style, new_style)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)

# Update all HTML files in the specified directory
update_html_files('scenes/', translation_value='-30%')
