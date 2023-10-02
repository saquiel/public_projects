

# 1/ add virtual env

# desactivate conda
conda deactivate

# install virtual env
pip3 install virtualenv

# change to working directory
# create virtual env
virtualenv -p python3 env

# activate virtual env
source venv_exporter/bin/activate
# windows
\Scripts\activate.bat
\Scripts\Activate.ps1


# git ignore virtual env
# edit:
.gitignore
# add:
env/


# 2/ depenancy file
# You install packages
pip install some-package
# create dependancy file
# cd to the app directory 
# will install the requirement in this folder => tracked by git
pip freeze > requirements.txt


# fixed library
pip show pandas
# in requirements.txt add the verison
pandas==1.2.4

# Install from requirements.txt
pip install -r requirements.txt





# remove
# desactivate virtual env
deactivate
rm -rf venv