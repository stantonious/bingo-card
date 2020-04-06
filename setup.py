'''
@author: bstaley
'''
import os
from distutils.core import setup

setup(name='mnist-bingo-card',
      version=1.0,
      install_requires=['flask',
                        'numpy',
                        'matplotlib',
                        ],
      description='''app to generate a bingo card using images from MNIST
                 ''',
      author='Bryan Staley',
      author_email='bryan.w.staley@gmail.com',
      scripts=['card_generator/app.py'],
      packages=['card_generator'],
      package_data={'card_generator':['data/*','templates/*'],},
      )
