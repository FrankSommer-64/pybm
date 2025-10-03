# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------
# pybm - Build-Tool für die Entwicklung von Python-Projekten.
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
CLI für pybm.
"""

import sys

from pybm import *
from pybm.deb import build_deb
from pybm.nsis import build_nsis
from pybm.rpm import build_rpm
from pybm.sign import build_sign
from pybm.util import build_env_for
from pybm.wheel import build_wheel
from pybm.custom import build_custom


def show_usage():
    """
    Zeigt Aufruf-Infos an.
    """
    print('Aufruf: pybm <Build-Typ> <Projekt> [<Feature-Set>]')
    print('  Build-Typen:')
    print('    build_wheel erzeugt ein Python wheel')
    print('    build_deb erzeugt ein Debian Installationspaket')
    print('    build_rpm erzeugt ein rpm Installationspaket')
    print('    build_nsis erzeugt einen NSIS Windows-Installer')
    print('    build_custom erzeugt ein ZIP-Archiv für die manuelle Installation')
    print('    build_sign generiert eine signierte Datei mit den SHA512-Hashes')
    print()


def check_feature_set(build_environment: dict, featureset: str = None):
    """
    Prüft das Feature-Set.
    :param build_environment: Build-Umgebung
    :param featureset: Name des Feature-Sets.
    :raises RuntimeException: falls es ein Problem mit dem Feature-Set gibt
    """
    if featureset == FEATURE_SET_ALL:
        # Feature-Set 'all' ist immer gut
        return
    if len(build_environment[PAR_FEATURE_SETS]) > 1:
        # Projekt mit Feature-Sets, es muss ein gültiger Wert dafür angegeben werden
        if featureset is None:
            raise RuntimeError('Feature-Set muss angegeben werden')
        if featureset not in build_environment[PAR_FEATURE_SETS]:
            raise RuntimeError(f'Feature-Set {featureset} existiert nicht')
    else:
        # Projekt ohne Feature-Sets, es darf keines angegeben werden
        if featureset is not None:
            raise RuntimeError('Projekt hat keine Feature-Sets')


def cli_main():
    """
    Hauptprogramm für die Kommandozeile.
    """
    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)
    build_type = sys.argv[1].lower()
    project = sys.argv[2]
    try:
        build_env = build_env_for(project)

        if build_type in (BUILD_TYPE_NSIS, BUILD_TYPE_SIGN, BUILD_TYPE_CUSTOM):
            feature_set_ignored = True
            feature_set = FEATURE_SET_ALL
        else:
            feature_set_ignored = False
            feature_set = None if len(sys.argv) == 3 else sys.argv[3].lower()
        check_feature_set(build_env, feature_set)
        if build_type == BUILD_TYPE_WHEEL:
            build_func = build_wheel
        elif build_type == BUILD_TYPE_DEB:
            build_func = build_deb
        elif build_type == BUILD_TYPE_RPM:
            build_func = build_rpm
        elif build_type == BUILD_TYPE_CUSTOM:
            build_func = build_custom
        elif build_type == BUILD_TYPE_NSIS:
            build_func = build_nsis
        elif build_type == BUILD_TYPE_SIGN:
            build_func = build_sign
        else:
            raise RuntimeError(f'Unbekannter Build-Typ {build_type}')
        if len(build_env[PAR_FEATURE_SETS]) == 0:
            build_func(build_env, project)
        else:
            if feature_set_ignored or feature_set != FEATURE_SET_ALL:
                build_func(build_env, project, feature_set)
            else:
                for _f in build_env[PAR_FEATURE_SETS]:
                    build_func(build_env, project, _f)
    except BaseException as _e:
        print(str(_e))
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
