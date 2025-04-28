# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """The setup script."""
#
# from setuptools import setup, find_packages
#
# with open('README.rst') as readme_file:
#     readme = readme_file.read()
#
# with open('HISTORY.rst') as history_file:
#     history = history_file.read()
#
# with open('requirements.txt') as requirements_file:
#     requirements = requirements_file.read()
#
# setup_requirements = [ ]
#
# test_requirements = [ ]
#
# setup(
#     author="Alexandr Vitruk",
#     author_email='a.vitruk@blackhub.games',
#     classifiers=[
#         'Development Status :: 3 - Alpha',
#         'Intended Audience :: Developers',
#         'License :: OSI Approved :: MIT License',
#         'Natural Language :: English',
#         'Programming Language :: Python :: 3.13',
#     ],
#     description="Python Node Editor using PySide6",
#     install_requires=requirements,
#     license="MIT license",
#     long_description=readme + '\n\n' + history,
#     include_package_data=True,
#     keywords='nodeeditor',
#     name='nodeeditor',
#     #packages=find_packages(include=['_template']),
#     packages=find_packages(include=['nodeeditor', 'nodeeditor.*'], exclude=['examples*', 'tests*']),
#     package_data={'': ['qss/*']},
#     setup_requires=setup_requirements,
#     test_suite='tests',
#     tests_require=test_requirements,
#     python_requires=">=3.13",
#
#     url='https://github.com/RaiderObject/template',
#     version="0.9.0",
#     zip_safe=False,
# )

from setuptools import setup

setup()