import json
import os

json_file_path = '/home/runner/work/Physicscore/Physicscore/Template.json'
os.path.isfile(json_file_path)
readme_file_path = '/home/runner/work/Physicscore/Physicscore/README.md'

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
