import ckan.plugins as plugins
import ckan.lib.plugins as libplugins
import ckan.plugins.toolkit as tk
import ckan.logic.schema
import datetime
import helpers as h
from model import create_table, get_package_review, add_package_review, update_package_review, GroupReview
from helpers import calculate_next_review_date
ValidationError = ckan.logic.ValidationError

#from ckan.lib.email_notifications import _notifications_functions
from ckan.lib.activity_streams import activity_stream_string_functions, activity_stream_string_icons


# def notifications(user_dict, since):
#     notifications = [{
#         'subject': 'This is a test',
#         'body': 'Yes it is'
#         }]
# 
#     return notifications

def activity_stream_string_review_package(context, activity):
    return plugins.toolkit._("{dataset} is due for review")

def activity_stream_string_package_reviewed(context, activity):
    return plugins.toolkit._("{dataset} has been reviewed")

class ReviewPlugin(plugins.SingletonPlugin, libplugins.DefaultOrganizationForm):
    """
    Setup plugin
    """
    print "loading ckanext-review"

    create_table()
    #_notifications_functions.append(notifications)
    activity_stream_string_functions['package reviewed'] = activity_stream_string_package_reviewed
    activity_stream_string_functions['review package'] = activity_stream_string_review_package
    activity_stream_string_icons['review package'] = 'calendar'
    
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    #plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IOrganizationController, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    
    """
    IRoutes
    """
    def before_map(self, map):

        map.connect('review', '/dataset/review/{id}',
            controller='ckanext.review.controller:ReviewController',
            action='index')

        return map
    
    """
    IConfigurer
    """
    def update_config(self, config):
        plugins.toolkit.add_template_directory(config, 'templates')
        plugins.toolkit._add_resource('fanstatic', 'fanstatic')
    
    """
    IGroupForm
    """
#     def is_fallback(self):
#         return False
#     
#     def group_types(self):
#         return ('organization',)
#     
#     def form_to_db_schema(self):
#         schema = super(ReviewPlugin, self).form_to_db_schema()
#         schema.update({
#                 'dataset_review_interval': [tk.get_validator('ignore_missing'), tk.get_validator('is_positive_integer'),
#                     tk.get_converter('convert_to_extras')]
#                 })
#         schema.update({
#                 'dataset_review_interval_type': [tk.get_validator('ignore_missing'),
#                     tk.get_converter('convert_to_extras')]
#                 })
#         return schema
#     
#     def db_to_form_schema(self):
#         schema = super(ReviewPlugin, self).db_to_form_schema()
#         if not schema:
#             schema = ckan.logic.schema.group_form_schema()
#             #schema = ckan.logic.schema.default_group_schema()
#             schema['num_followers'] = [tk.get_validator('ignore_missing')]
#             schema['package_count'] = [tk.get_validator('ignore_missing')]
#             schema.update({
#                 'dataset_review_interval': [tk.get_converter('convert_from_extras'),
#                     tk.get_validator('ignore_missing'), tk.get_validator('is_positive_integer')]
#                 })
#             schema.update({
#                 'dataset_review_interval_type': [tk.get_converter('convert_from_extras'),
#                     tk.get_validator('ignore_missing')]
#                 })
#         return schema
#     
#     def check_data_dict(self, data_dict):
#         dataset_review_interval = data_dict.get('dataset_review_interval', None)
#     
#     def setup_template_variables(self, context, data_dict):
#         super(ReviewPlugin, self).setup_template_variables(context, data_dict)
#         
#         tk.c.dataset_review_interval_types = ('day(s)', 'week(s)', 'month(s)', 'year(s)')
        
    """
    IOrganizationController
    """
    def read(self, entity):
        if isinstance(entity, ckan.model.Group):
            gr = ckan.model.Session.query(GroupReview).filter(GroupReview.group_id == entity.id).first()
            if gr:
                tk.c.dataset_review_interval = gr.dataset_review_interval
                tk.c.dataset_review_interval_type = gr.dataset_review_interval_type
        return entity
    
    def create(self, entity):
        
        if isinstance(entity, ckan.model.Group):
            gr = ckan.model.Session.query(GroupReview).filter(GroupReview.group_id == entity.id).first()
            
            if gr is None:
                gr = GroupReview()
                gr.group_id = entity.id
                gr.dataset_review_interval = tk.request.params.getone('dataset_review_interval')
                gr.dataset_review_interval_type = tk.request.params.getone('dataset_review_interval_type')
                
                is_valid, errors = gr.validate()
                
                if is_valid:
                    gr.save()
                else:
                    raise ValidationError(errors)
                
    def edit(self, entity):
        if isinstance(entity, ckan.model.Group):
            
            gr = ckan.model.Session.query(GroupReview).filter(GroupReview.group_id == entity.id).first()
            if gr is None:
                gr = GroupReview()
                gr.group_id = entity.id
                gr.dataset_review_interval = tk.request.params.getone('dataset_review_interval')
                gr.dataset_review_interval_type = tk.request.params.getone('dataset_review_interval_type')
                
                is_valid, errors = gr.validate()
                
                if is_valid:
                    gr.save()  
                else:
                    raise ValidationError(errors)
            else:
                gr.dataset_review_interval = tk.request.params.getone('dataset_review_interval')
                gr.dataset_review_interval_type = tk.request.params.getone('dataset_review_interval_type')
                
                is_valid, errors = gr.validate()
                
                if is_valid:
                    gr.commit()
                else:
                    raise ValidationError(errors)
                      
    """
    IPackageController
    """       
    def after_show(self, context, pkg_dict):
        #set the default review date value
        if 'owner_org' in pkg_dict:
            package_review = get_package_review(context['session'], pkg_dict['id'])
            #if package already has a review date set, return it...
            if package_review: #and package_review.next_review_date > datetime.date.today():
                db_date = package_review.next_review_date
                #format date to an AU format
                pkg_dict['next_review_date'] = datetime.datetime.strftime(db_date, '%d-%m-%Y')
                pkg_dict['needs_review'] = package_review.next_review_date <= datetime.date.today()
            #otherwise calculate the default date...
            elif pkg_dict['owner_org']:
                review_date = calculate_next_review_date(context, pkg_dict['owner_org'])

                #format date to an AU format
                au_date = datetime.datetime.strftime(review_date, '%d-%m-%Y')
                pkg_dict['next_review_date'] = str(au_date) if 'for_view' not in context else ''
                pkg_dict['needs_review'] = True

#     def after_search(self, search_results, data_dict):
#         for r in search_results['results']:
#             r['next_review_date'] = str(datetime.date.today())
                    
    def after_update(self, context, pkg_dict):
        package_review = get_package_review(context['session'], pkg_dict['id'])
        if 'next_review_date' in tk.request.params:
            try:
                next_review_date = datetime.datetime.strptime(tk.request.params.getone('next_review_date'), '%d-%m-%Y').date()
            except ValueError:
                context['session'].rollback()
                raise ValidationError({'next_review_date' : ['Must be a valid date (dd-mm-yyyy)']})
            
            if package_review:
                package_review.next_review_date = next_review_date
                update_package_review(context['session'], package_review)
            else:
                add_package_review(context['session'], pkg_dict['id'], next_review_date)
                
    """
    ITemplateHelpers
    """
    def get_helpers(self):
        return {
            'get_dataset_review_interval_types'             : h.get_dataset_review_interval_types,
                }