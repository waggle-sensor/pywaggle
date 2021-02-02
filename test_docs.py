from pathlib import Path
import re
import subprocess
import logging
import sys
import unittest


def run_python_code_block(code):
    return subprocess.check_output(['python3', '-s'], input=code.encode())


class TestDocs(unittest.TestCase):

    def test_python_scripts(self):
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
                        f'code block failed in "{path}"\n\n```python{code}```\n\n')
                    raise


if __name__ == "__main__":
    unittest.main()
