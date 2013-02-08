from distutils.core import setup

setup(
    name='django-ctt',
    version='0.1',
    packages=['tests', 'tests.testapp', 'ctt'],
    url='http://www.hiddendata.co/',
    license='HDL',
    author='Hiddendata',
    author_email='g.szczepanczyk@hiddendata.co',
    description='Implementation of sql trees with Closure Table'
)
