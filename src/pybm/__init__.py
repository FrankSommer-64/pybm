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

# pybm Version
VERSION = '0.9.2'

# Build-Typen
BUILD_TYPE_DEB = 'build_deb'
BUILD_TYPE_RPM = 'build_rpm'
BUILD_TYPE_WHEEL = 'build_wheel'
BUILD_TYPE_NSIS = 'build_nsis'
BUILD_TYPE_SIGN = 'build_sign'
BUILD_TYPE_CUSTOM = 'build_custom'

# Build-Parameter
PAR_FEATURE_SETS = 'feature-sets'
PAR_PACKAGE_NAME = 'package-name'
PAR_PROJECT_ROOT = 'project-root'
PAR_PROJECT_VERSION = 'project-version'
PAR_TESTING_ROOT = 'testing-root'
PAR_VENV_PATH = 'venv-path'

# Umgebungsvariablen
ENVA_NSIS_PATH = 'PYBM_NSIS_PATH'
ENVA_PROJECTS_ROOT = 'PYBM_PROJECTS_ROOT'
ENVA_TESTING_ROOT = 'PYBM_TESTING_ROOT'
ENVA_VENV_PATH = 'PYBM_VENV_PATH'

# Diverses
FEATURE_SET_ALL = 'all'
WHEEL_CFG_FILE_NAME = 'pyproject.toml'
