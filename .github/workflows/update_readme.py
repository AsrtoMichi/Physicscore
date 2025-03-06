import json
import os

# Percorsi dei file
json_file_path = 'path/to/your/config.json'
readme_file_path = 'README.md'
temp_readme_file_path = 'README_temp.md'

# Leggi il contenuto del file JSON
with open(json_file_path, 'r') as json_file:
    json_content = json.load(json_file)

# Converti il contenuto del file JSON in una stringa formattata
json_string = json.dumps(json_content, indent=4)

# Leggi il contenuto del README.md originale
with open(readme_file_path, 'r') as readme_file:
    readme_content = readme_file.read()

# Inserisci il contenuto del file JSON nel README.md
placeholder = '<!-- INSERT JSON HERE -->'
updated_readme_content = readme_content.replace(placeholder, f'```json\n{json_string}\n```')

# Scrivi il contenuto aggiornato in un file temporaneo
with open(temp_readme_file_path, 'w') as temp_readme_file:
    temp_readme_file.write(updated_readme_content)

# Sostituisci il file README.md originale con il file temporaneo
os.replace(temp_readme_file_path, readme_file_path)
