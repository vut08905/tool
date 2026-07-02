# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

block_cipher = None
try:
    from PyInstaller.archive.pyi_crypto import PyiBlockCipher
    block_cipher = PyiBlockCipher(key='UlsaAutomation24')
except ImportError:
    pass

datas = [('automation', 'automation')]
binaries = []
hiddenimports = [
    'PIL', 'qrcode', 'requests',
    'automation.auto_login_with_title_check',
    'automation.auto_with_save',
    'automation.config_auto_login',
    'automation.enhanced_two_step_registration',
    'automation.handle_schedule_conflict',
    'automation.real_website_automation',
    'automation.two_step_registration'
]
tmp_ret = collect_all('selenium')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('webdriver_manager')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['complete_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
    cipher=block_cipher,
)

# Loại bỏ file mã nguồn thô
a.datas = [x for x in a.datas if not x[0].endswith(('.py', '.pyc', '.pyo'))]

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dangkytinchiulsa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
