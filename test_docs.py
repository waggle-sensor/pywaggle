from pathlib import Path
import re
import subprocess
import logging
import sys


def run_python_code_block(code):
    return subprocess.check_output(['python3', '-s'], input=code.encode())


exitcode = 0

for path in Path('.').glob('**/*.md'):
    text = path.read_text()
    for code in re.findall('```python(.*?)```', text, re.S):
        try:
            print(f'running {path}')
            run_python_code_block(code)
        except Exception as exc:
            exitcode = 1
            logging.exception(
                f'code block failed in {path}\n\n```python{code}```\n\n')

sys.exit(exitcode)
