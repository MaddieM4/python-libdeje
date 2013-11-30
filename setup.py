#!/usr/bin/env python

from distutils.core import setup

setup(
	name = 'deje',
	version = '0.1.2',
	description = 'Democratically Enforced JSON Environment library',
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/python-libdeje/',
    scripts = [
        'deje/dexter/dexter',
    ],
	packages = [
		'deje',
		'deje.dexter',
		'deje.dexter.commands',
		'deje.interpreters',
		'deje.handlers',
		'deje.tests',
	],
)
