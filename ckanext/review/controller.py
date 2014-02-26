
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

from helpers import calculate_next_review_date
from model import create_table, get_package_review, add_package_review, update_package_review

class ReviewController(BaseController):
    """
    ckanext-review controller
    """

    def index(self, id):
        
        if ckan.plugins.toolkit.request.method == 'POST':
            context = {'model': ckan.model,
                       'session': ckan.model.Session,
                       'user': pylons.c.user or pylons.c.author}
            
            data_dict = {'id': id}
            
            #check access
            try:
                plugins.toolkit.check_access('package_update', context, data_dict)
            except plugins.toolkit.NotAuthorized:
                plugins.toolkit.abort(401, plugins.toolkit._('Unauthorized to review this package'))
            
            #get package
            try:
                pkg_dict = plugins.toolkit.get_action('package_show')(context, data_dict)
            except plugins.toolkit.ObjectNotFound:
                plugins.toolkit.abort(404, plugins.toolkit._('Dataset not found'))
            except plugins.toolkit.NotAuthorized:
                plugins.toolkit.abort(401, plugins.toolkit._('Unauthorized to read package %s') % id)
            
            #calculate next review date
            next_review_date = calculate_next_review_date(context, pkg_dict['owner_org'])
            
            #update review date...
            package_review = get_package_review(context['session'], pkg_dict['id'])
            
            if package_review:
                package_review.next_review_date = next_review_date
                update_package_review(context['session'], package_review)
            else:
                add_package_review(context['session'], pkg_dict['id'], next_review_date)
              
            #commit
            context['session'].commit()  
        
        #return to view screen
        ckan.plugins.toolkit.redirect_to(controller="package", action="read", id=id)
