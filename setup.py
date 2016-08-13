from setuptools import setup

setup(name='sleepyq',
      version='0.2',
      description='SleepIQ API for Python',
      url='http://github.com/technicalpickles/sleepyq',
      author='Josh Nichols',
      author_email='josh@technicalpickles.com',
      license='MIT',
      packages=['sleepyq'],
      install_requires=[
          'requests'
      ],
      zip_safe=False)
