#!/usr/bin/env python3
"""สร้าง .github/workflows/mae-windows.yml จาก flutter-build.yml ของ RustDesk

เอาเฉพาะ: bridge, TopMostWindow (x64), build-for-windows-flutter (x64) จนถึงขั้นแพ็ก .exe
ตัด: แพลตฟอร์มอื่น, ARM64, MSI, release upload  ผลลัพธ์: artifact MAERemote-<ver>-x86_64.exe
ใช้: python3 gen-workflow.py <rustdesk-source-dir>
"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]).resolve()
src = (root / '.github/workflows/flutter-build.yml').read_text(encoding='utf-8').splitlines()


def find(pred, start=0, what=''):
    for i in range(start, len(src)):
        if pred(src[i]):
            return i
    sys.exit(f'STOP: marker not found: {what}')


jobs_i = find(lambda l: l == 'jobs:', what='jobs:')
env_i = find(lambda l: l == 'env:', what='env:')
bridge_i = find(lambda l: l == '  generate-bridge:', what='generate-bridge')
top_i = find(lambda l: l == '  build-RustDeskTempTopMostWindow:', what='topmost job')
win_i = find(lambda l: l == '  build-for-windows-flutter:', what='windows job')
msbuild_i = find(lambda l: l.strip() == '- name: Add MSBuild to PATH', win_i, 'Add MSBuild step')

header = [
    'name: MAE Remote - Windows build',
    '',
    '# สร้างจาก flutter-build.yml ของ RustDesk ด้วย gen-workflow.py (อย่าแก้มือ ให้แก้สคริปต์แล้วสร้างใหม่)',
    'on:',
    '  workflow_dispatch:',
    '    inputs:',
    '      upload-artifact:',
    '        type: boolean',
    '        default: true',
    '      upload-tag:',
    '        type: string',
    '        default: "mae"',
    '',
]
env_block = src[env_i:jobs_i]
# SIGN_BASE_URL ว่าง -> "-2" -> ขั้น sign ถูกข้าม (เราไม่มีบริการ sign ของ RustDesk)
body = ['jobs:'] + src[bridge_i:top_i] + src[top_i:win_i] + src[win_i:msbuild_i]
text = '\n'.join(header + env_block + body)


def drop_matrix_entry(text, marker):
    # ลบ "- { ... marker ... }" หนึ่งก้อนใน matrix
    pat = re.compile(r'\n( +)- \{[^}]*' + re.escape(marker) + r'[^}]*\}')
    new, n = pat.subn('', text, count=1)
    if n != 1:
        sys.exit(f'STOP: matrix entry not found: {marker}')
    return new


text = drop_matrix_entry(text, 'platform: ARM64')
text = drop_matrix_entry(text, 'target: aarch64-pc-windows-msvc')

old = './SignOutput/rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.exe'
if text.count(old) != 1:
    sys.exit('STOP: portable exe output line changed upstream')
text = text.replace(old, './SignOutput/MAERemote-${{ env.VERSION }}-${{ matrix.job.arch }}.exe')
text += '''
      - name: Upload MAE Remote installer
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: MAERemote-windows-${{ matrix.job.arch }}
          path: ./SignOutput/MAERemote-*.exe
          if-no-files-found: error
'''
out = root / '.github/workflows/mae-windows.yml'
out.write_text(text, encoding='utf-8')
print(f'wrote {out} ({len(text.splitlines())} lines)')
