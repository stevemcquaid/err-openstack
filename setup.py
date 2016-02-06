#!/usr/bin/env python
import re
from setuptools import setup, find_packages
from os import path

REGEX = '^([\w\-\.]+)[\s]*([=<>\!]+)[\s]*([0-9\.]+)+(,[<>\!=]+[0-9\.]+)*'


def required_packages_list(file_name, exclude_version=False):
    parent = path.abspath('.')
    if not file_name:
        raise RuntimeError('Pass the requirements.txt from where requires '
                           'list will be generated')
    full_path = path.join(parent, file_name)
    print ("Requirements file %s" % full_path)
    pattern = re.compile(REGEX)
    requires_list = []
    contents = None
    with open(full_path) as f:
        contents = f.read()

    for line in contents.splitlines():
        match = pattern.match(line)
        if match:
            if exclude_version:
                requires_list.append(match.group(1))
            else:
                requires_list.append(match.group())

    print ('Requires List %r' % requires_list)
    return requires_list

setup(
    name='gdopenstack',
    author='Cloud errbot plugin',
    author_email='smcquaid@godaddy.com',
    summary='GD Openstack errbot plugin',
    description_file='README.md',
    license='Internal Use Only',
    version='1.1.1',
    install_requires=required_packages_list('requirements.txt'),
    packages=find_packages(
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']))
