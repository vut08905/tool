# -*- mode: python ; coding: utf-8 -*-
# File cấu hình PyInstaller cho ULSA Automation
# Sử dụng: pyinstaller complete_gui.spec

block_cipher = None

# Danh sách data files cần include
added_files = [
    ('automation', 'automation'),
    ('b1.html', '.'),
    ('b11.html', '.'),
    ('b111.html', '.'),
    ('b2.html', '.'),
    ('b2_1.html', '.'),
    ('b22.html', '.'),
    ('b3.html', '.'),
    ('b33.html', '.'),
]

a = Analysis(
    ['complete_gui.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'tkinter',
        'pandas',
        'fuzzywuzzy',
        'Levenshtein',
        'selenium',
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.random._examples',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ULSA_DangKyTinChi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Nén file exe (giảm kích thước)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Không hiện console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Thêm icon nếu có: icon='icon.ico'
)
