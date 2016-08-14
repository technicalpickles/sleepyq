from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sleepyq',
      version='0.4',
      description='SleepIQ API for Python',
      long_description=readme(),
      url='http://github.com/technicalpickles/sleepyq',
      author='Josh Nichols',
      author_email='josh@technicalpickles.com',
      license='MIT',
      packages=['sleepyq'],
      install_requires=[
          'requests'
      ],
      include_package_data=True,
      zip_safe=False)
