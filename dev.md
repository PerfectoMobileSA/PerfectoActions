# PerfectoActions

## Steps to contribute to this python package by testing it in test pypi:

Increase the version in setup.py and run the following to upload to test pypi: <br /> 

    python3 -m pip install --user --upgrade setuptools wheel twine
    
    pipreqs . --force
    python3 setup.py install
    rm -rf build dist
    python3 setup.py clean --all
    python3 setup.py sdist bdist_wheel
    python3 -m twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/* -r testpypi
    
    ** below is applicable only for pushing the package to main pypi:
    rm -rf build dist
    python3 setup.py clean --all
    python3 setup.py sdist bdist_wheel
    python3 -m twine upload dist/*

Using Python’s Virtual for testing:<br /> 

    source ~/.bash_profile 
    python3 -m pip install --user --upgrade virtualenv
    virtualenv env
    source env/bin/activate
    
    ** to stop:
    deactivate

Install test package in local:<br /> 

    pip3 uninstall perfectoactions
    pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple perfectoactions -U

    ** below is applicable only for pushing the package to main pypi:
    pip3 install perfectoactions -U
    
    Mac: 
    python3 -m pip install perfectoactions -U

    
Python code performance check:<br /> 

    Navigate to perfecto folder in terminal/cmd. 
    pip install snakeviz
    python3 -m cProfile -o temp.dat perfectoactions.py -c ps -s "---" 
    snakeviz temp.dat