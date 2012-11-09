#!/usr/bin/env python

from distutils.core import setup

setup(
	name = 'deje',
	version = '0.0.1',
	description = 'Democratically Enforced JSON Environment library',
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/python-libdeje/',
    #scripts = [
    #    'scripts/ejtpd',
    #],
	packages = [
		'deje',
		'deje.interpreters',
		'deje.handlers',
	],
)
