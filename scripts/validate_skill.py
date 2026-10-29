"""Validate this package's deliberately small, flat skill metadata format."""

from pathlib import Path
import re
import sys


def validate(root):
    root = Path(root)
    text = (root / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---\r?\n(.+)', text, re.DOTALL)
    if not match:
        raise ValueError('Missing skill metadata or instructions')
    fields = {}
    for line in match[1].splitlines():
        key, separator, value = line.partition(': ')
        if not separator or key in fields or not value.strip():
            raise ValueError('Expected unique, nonempty flat metadata fields')
        fields[key] = value.strip()
    if set(fields) != {'name', 'description'}:
        raise ValueError('Expected name and description only')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name']):
        raise ValueError('Invalid skill name')
    if len(fields['name']) > 64 or len(fields['description']) > 1024:
        raise ValueError('Metadata too long')
    if '[TODO:' in text:
        raise ValueError('Unfinished instructions')
    for file in root.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            resolved = (file.parent / target.split('#', 1)[0]).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                raise ValueError(f'Invalid local reference in {file.relative_to(root)}')


if __name__ == '__main__':
    try:
        validate(Path(__file__).resolve().parents[1])
    except (ValueError, OSError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
    print('PASS: skill metadata and local references')
