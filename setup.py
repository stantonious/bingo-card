'''
@author: bstaley
'''
import os
from distutils.core import setup

setup(name='mnist-bingo-card',
      version=1.0,
      install_requires=['flask',
                        'numpy',
                        'jinja',
                        'matplotlib',
                        ],
      description='''app to generate a bingo card using images from MNIST
                 ''',
      author='Bryan Staley',
      author_email='bryan.w.staley@gmail.com',
      scripts=['card-generator/app.py'],
      packages=['card-generator'],
      package_data={'card-generator':['data/*','templates/*'],},
      )
