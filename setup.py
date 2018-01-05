# -*- coding: utf-8 -*-
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

requires = ['click==6.7', 'pytest']
tests_require = ['pytest', 'pytest-cache', 'pytest-cov']


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name='pwned_check',
      version='0.1',
      description='pwned_check package',
      url='http://github.com/truc/pwned_check',
      author='Pwned Check',
      author_email='test@example.com',
      license='MIT',
      packages=['pwned_check'],
      zip_safe=False,
      install_requires=requires,
      entry_points={'console_scripts': ['pwned_check = pwned_check.cli:main']},
      classifiers=[
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ],
      extras_require={'test': tests_require},
      cmdclass={'test': PyTest},
      )
