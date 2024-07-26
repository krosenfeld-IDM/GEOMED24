# GEOMED24

## Installation

First, `laser`
```
pip install git+https://github.com/InstituteforDiseaseModeling/laser.git@3c5f0e3cafbb22abd62f55ee82db7e9a3b3fa792
```
then other dependencies:
```
pip install -r requirements.txt --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
and make sure that PYTHONPATH is set to include `scenarios/` e.g.,:
```
mamba env config vars set PYTHONPATH=".:./scenarios"
```

## References
- Data from: https://github.com/InstituteforDiseaseModeling/EMOD-Generic-Scripts/tree/main/model_measles_nga01/Assets