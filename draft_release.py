import os
import requests
import waggle
import json
import subprocess

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'requests',
}

name = f'v{waggle.__version__}'

subprocess.check_output(['git', 'tag', '-a', name, '-m', f'drafting {name} release'])

data = json.dumps({
    'draft': True,
    'name': name,
    'tag_name': name,
    'body': f'Draft of release {name}.'
})

print(f'Drafting release {name}...')

r = requests.post(
    url='https://api.github.com/repos/waggle-sensor/pywaggle/releases',
    auth=('token', GITHUB_TOKEN),
    headers=headers,
    data=data)

r.raise_for_status()
print(r.json())
