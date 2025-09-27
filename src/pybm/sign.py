# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------
# pybm - Tools für die Entwicklung von Python-Projekten.
#
# Copyright (c) 2025, Frank Sommer.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------------------------

"""
Erzeugt eine Datei mit den SHA512-Hashes aller Dateien im dist-Verzeichnis eines Projekts.
Zur Datei wird eine PGP-Signatur erstellt.
"""

import hashlib
import os

from pybm import *
from pybm.util import shell_cmd


SHA512_FILE_NAME = 'SHA512SUMS'
SHA512_SIG_FILE_NAME = f'{SHA512_FILE_NAME}.sign'


def build_sign(build_environment: dict, _project: str, _feature_set: str = None):
    """
    Erzeugt Datei SHA512SUMS mit den Hashes aller Dateien im dist-Verzeichnis des Projekts,
    je eine Zeile <Hash> <Dateiname>.
    :param build_environment: Build-Environment
    :param _project: Name des Projekts
    :param _feature_set: optional Name des Feature-Sets
    """
    _project_root = build_environment[PAR_PROJECT_ROOT]
    _dist_path = os.path.join(_project_root, 'dist')
    _hashes = []
    for _file_name in os.listdir(_dist_path):
        if _file_name == SHA512_FILE_NAME or _file_name == SHA512_SIG_FILE_NAME:
            continue
        with open(os.path.join(_dist_path, _file_name), 'rb') as _f:
            _hash = hashlib.file_digest(_f, 'sha512')
            _hashes.append(f'{_hash.hexdigest()} {_file_name}{os.linesep}')
    _sha512_file_path = os.path.join(_dist_path, SHA512_FILE_NAME)
    _sha512_sig_file_path = os.path.join(_dist_path, SHA512_SIG_FILE_NAME)
    with open(_sha512_file_path, 'w') as _f:
        _f.writelines(_hashes)
    _cmd = ['gpg', '--armor', '--output', _sha512_sig_file_path, '--detach-sign', _sha512_file_path]
    _rc = shell_cmd(_cmd)
    if _rc != 0:
        raise RuntimeError(f'Konnte Datei {SHA512_FILE_NAME} nicht signieren')
    print(f'Datei {SHA512_FILE_NAME} mit Signatur erstellt.')
