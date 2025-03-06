import json
import os


json_file_path = '/home/runner/work/Physicscore/Physicscore/Template.json'
readme_file_path = '/home/runner/work/Physicscore/Physicscore/README.md'

json_string = json.dumps(json.load(open(json_file_path, 'r')), indent=4)

updated_readme_content = open(readme_file_path, 'r').read().replace('<!-- INSERT JSON HERE -->', f'```json\n{json_string}\n```')

open(readme_file_path, 'w').write(updated_readme_content)
