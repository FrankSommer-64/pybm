[![Contributors][contributors-shield]][contributors-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<br />
<div align="center">
  <a href="https://github.com/FrankSommer-64/pybm">
    <img src="images/pybm.png" alt="Logo" width="128" height="128">
  </a>

<h3 align="center">pybm</h3>
  <p align="center">
    Simple wrapper library to automate build tasks for Python projects.
    <br />
    <a href="https://github.com/FrankSommer-64/pybm"><strong>Documentation</strong></a>
    <br />
    <br />
    <a href="https://github.com/FrankSommer-64/pybm/issues">Report Bug</a>
    ·
    <a href="https://github.com/FrankSommer-64/pybm/issues">Request Feature</a>
  </p>
</div>


## About The Project

Simple build manager for Python projects.

## Getting Started

### Prerequisites

Pybm needs Python, version 3.10 or higher and hatchling.
Pybm has been tested on Linux Mint 22, Fedora 42 and Windows 11.
My PGP-Key frank.sommer@sherpa-software.de is available on https://keys.openpgp.org.


### Installation

1. Create Python virtual environment for pybm
2. Download pybm wheel, scripts, SHA512SUMS and SHA512SUMS.sign
3. Verify PGP signature for SHA512SUMS
4. Verify SHA512 hash for pybm wheel is correct
5. Install wheel into Python virtual environment using pip
6. Extract pybm scripts into a directory in your PATH (e.g. $HOME/bin)


### Configuration
Pybm requires a project structure as below. Under build subdirectory wheel is always
needed, the others only for the corresponding target platform.

    build
      |- deb (files to build a debian package: control, data, debian-binary)
      |- nsis (files to build NSIS Windows installer: .nsi)
      |- rpm (files to build an RPM package: SOURCES, SPECS)
      |- wheel (pyproject.toml)
      |- custom (data for manual installation)
    dist (receives packages built by pybm)
    src (Python sources)
      |- <project> (same as project root directory name)
         |- <package> (project package)
         |- ...

If the project comes with different features (e.g. one package for core functionality,
another with full functionality including a GUI), the build subdirectory must be changed to

    build
      |- featuresets
           |- <featureset1>
                |- deb
                |- ...
           |- <featureset2>
                |- deb
                |- ...

pybm requires two environment variables to be set:
PYBM_PROJECTS_ROOT must point to root directory for projects (e.g. $HOME/GITROOT)
PYBM_VENV_PATH must point to the Python virtual environment for pybm (e.g. $HOME/.python_venv/pybm)


## Usage

Command line interface:

- Create Python wheel: ```build_py wheel <project> [<feature-set>]```
- Create Debian install package: ```build_py deb <project> [<feature-set>]```
- Create RPM install package: ```build_py rpm <project> [<feature-set>]```
- Create NSIS Windows installer: ```build_py nsis <project>```
- Create custom ZIP archive: ```build_py custom <project>```
- Create hashes and signature: ```build_py sign <project>```
- Change owner of Debian package to root: ```sudo chroot_deb <deb-file>```

See [open issues](https://github.com/FrankSommer-64/pybm/issues) for a full list of proposed features (and known issues).


## Contributing

Any contributions you make are **greatly appreciated**.



## License

Distributed under the MIT License. See [LICENSE][license-url] for more information.



## Contact

Frank Sommer - Frank.Sommer@sherpa-software.de

Project Link: [https://github.com/FrankSommer-64/pybm](https://github.com/FrankSommer-64/pybm)

[contributors-shield]: https://img.shields.io/github/contributors/FrankSommer-64/pybm.svg?style=for-the-badge
[contributors-url]: https://github.com/FrankSommer-64/pybm/graphs/contributors
[issues-shield]: https://img.shields.io/github/issues/FrankSommer-64/pybm.svg?style=for-the-badge
[issues-url]: https://github.com/FrankSommer-64/pybm/issues
[license-shield]: https://img.shields.io/github/license/FrankSommer-64/pybm.svg?style=for-the-badge
[license-url]: https://github.com/FrankSommer-64/pybm/blob/master/LICENSE
