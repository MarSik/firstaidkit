from distutils.core import setup
import glob

setup(name='firstaidkit',
      version='0.1.0',
      description='System Rescue Tool',
      author='Joel Andres Granados',
      author_email='jgranado@redhat.com',
      url='http://fedorahosted.org/firstaidkit',
      license='GPLv2',
      packages = ['pyfirstaidkit'],
      scripts = ['firstaidkit']
      )

