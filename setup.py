from setuptools import setup, find_packages
import os

version = '0.1'

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).read()
changelog = open(os.path.join(base, 'CHANGELOG.rst')).read()
todo = open(os.path.join(base, 'TODO.rst')).read()

setup(name='riddler',
      version=version,
      description='',
      long_description=readme + '\n' + changelog + '\n' + todo,
      classifiers=[],
      keywords='interview job django',
      author='Antoine Millet',
      author_email='antoine@inaps.org',
      url='https://github.com/NaPs/Riddler',
      license='MIT',
      data_files=(
          ('/etc/', ('etc/riddler.conf',)),
      ),
      scripts=['riddleradm'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[])
