
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
from ckan.logic.validators import object_id_validators

from helpers import calculate_next_review_date, create_review_activity
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
                plugins.toolkit.check_access('package_review', context, data_dict)
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

            #create activity
            create_review_activity(context, pkg_dict)

            '''
            context = {'model': ckan.model,
           'session': ckan.model.Session,
           'ignore_auth': True}

            admin_user = plugins.toolkit.get_action('get_site_user')(context,{})

            object_id_validators['package reviewed'] = plugins.toolkit.get_validator('user_id_exists')#tk.get_validator('package_id_exists')

            activity_dict = {
                'user_id': admin_user['name'],
                'object_id': pkg_dict["creator_user_id"],
                'data' : { 'dataset': pkg_dict },
                'activity_type': 'package reviewed',
            }

            plugins.toolkit.get_action('activity_create')(context, activity_dict)
            '''
        
        #return to view screen
        ckan.plugins.toolkit.redirect_to(controller="package", action="read", id=id)
