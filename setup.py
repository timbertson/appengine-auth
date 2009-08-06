#!/usr/bin/env python

from setuptools import *

setup(
	name='appengine_auth',
	version='0.1.0',
	description='Google App Engine authorisation for non-web based python applications',
	author='Tim Cuthbertson',
	author_email='tim3d.junk+gae-auth@gmail.com',
	url='http://github.com/gfxmonk/appengine_auth/tree',
	py_modules=['appengine_auth'],
	
	classifiers=[
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Libraries :: Python Modules",
		],
	keywords='google appengine gae authentication login',
	license='Apache',
	install_requires=[
		'setuptools',
	],
)
