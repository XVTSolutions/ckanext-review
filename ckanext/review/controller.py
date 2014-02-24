
import sys
import os
import datetime
from operator import itemgetter

import pylons
import ckan

import ckan.lib.helpers as h
import ckan.plugins as plugins
from ckan.lib.base import BaseController
from ckan.lib.helpers import dataset_link, dataset_display_name
from ckan.lib.helpers import flash_error, flash_success, flash_notice
from ckan.logic.validators import package_name_exists
from ckan.logic.converters import convert_package_name_or_id_to_id as convert_to_id

class ReviewController(BaseController):
    """
    ckanext-review controller
    """

    def index(self, id):
        return plugins.toolkit.render("review/index.html")
