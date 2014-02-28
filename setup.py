from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-review',
	version=version,
	description="",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Andrew Dean',
	author_email='andrew at xvt.com.au',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
        'python-dateutil'
	],
	entry_points=\
	"""
        [ckan.plugins]
	review=ckanext.review.plugin:ReviewPlugin
	
		[paste.paster_command]
	notify=ckanext.review.commands.notify:NotifyCommand
	""",
)
