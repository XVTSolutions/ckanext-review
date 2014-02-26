ckanext-review
==============
Allows datasets to be reviewed at a set interval.

+ Adds a 'package_review' table to the database to store data related to the review process.
+ Adds a 'Dataset Review Interval' field to organisations that allows users to set the default review period for datasets.
+ Adds a 'Next Review' field to dataset new/edit screens which defaults to today + 'Dataset Review Interval'
+ Adds a 'Mark as Reviewed' button to dataset view page.

Installation
-------------
1. clone this repository
2. install: `python ckanext-review/setup.py develop`
3. add `review` to the list of plugins in .ini file

