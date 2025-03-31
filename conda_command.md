ENVNAME=python_class_env
conda create --name ENVNAME python=3.10
conda activate ENVNAME
conda install conda-forge::rasterio (install package from conda-forge channel)
conda env export --name python_class_env > environment.yml
conda env export --from-history > env_from_history.yml
conda install conda-forge::geopandas
conda env export --name python_class_env > environment.yml
conda env export --from-history > env_from_history.yml