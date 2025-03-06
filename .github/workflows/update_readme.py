import json
import os


def display_tree(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

# Replace 'your_directory_path' with the path of the directory you want to display
display_tree('your_directory_path')


json_file_path = '/home/runner/work/Physicscore/Template.json'
readme_file_path = '/home/runner/work/Physicscore/README.md'

# Leggi il contenuto del file JSON
with open(json_file_path, 'r') as json_file:
    json_content = json.load(json_file)

# Converti il contenuto del file JSON in una stringa formattata
json_string = json.dumps(json_content, indent=4)

# Leggi il contenuto del README.md originale
with open(readme_file_path, 'r') as readme_file:
    readme_content = readme_file.read()

# Inserisci il contenuto del file JSON nel README.md
updated_readme_content = readme_content.replace('<!-- INSERT JSON HERE -->', f'```json\n{json_string}\n```')

# Scrivi il contenuto aggiornato nel README.md
with open(readme_file_path, 'w') as readme_file:
    readme_file.write(updated_readme_content)
