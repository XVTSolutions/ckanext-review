import ckan.plugins as plugins
import ckan.lib.plugins as libplugins
import ckan.plugins.toolkit as tk
import ckan.logic.schema
import ckan.logic.auth as logic_auth
import ckan.logic.converters as converters
from ckan.logic import auth_sysadmins_check
import datetime
import helpers as h
from model import create_table, get_package_review, add_package_review, update_package_review, GroupReview
from helpers import calculate_next_review_date, ckanext_review_get_next_review_date
ValidationError = ckan.logic.ValidationError



# def notifications(user_dict, since):
#     notifications = [{
#         'subject': 'This is a test',
#         'body': 'Yes it is'
#         }]
# 
#     return notifications


class ReviewPlugin(plugins.SingletonPlugin, libplugins.DefaultOrganizationForm):
    """
    Setup plugin
    """
    print "loading ckanext-review"

    create_table()
    h.register_activity_types()

    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    #plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IOrganizationController, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)

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
        #print '**********after_show***************'
        #self._trace(context, pkg_dict)
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
                    
    def _update_extra(self, context, pkg_dict):
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
                

    def after_update(self, context, pkg_dict):
        #print '**********after_update***************'
        #self._trace(context, pkg_dict)
        self._update_extra(context, pkg_dict)
        return super(ReviewPlugin, self).after_update(context, pkg_dict)
                
    def after_create(self, context, pkg_dict):
        #print '**********after_update***************'
        #self._trace(context, pkg_dict)
        self._update_extra(context, pkg_dict)
        return super(ReviewPlugin, self).after_create(context, pkg_dict)

    """
    ITemplateHelpers
    """
    def get_helpers(self):
        return {
            'get_dataset_review_interval_types'             : h.get_dataset_review_interval_types,
            'ckanext_review_get_next_review_date'           : h.ckanext_review_get_next_review_date,
                }
        
        
    """   
    IAuthFunctions
    """ 
    def get_auth_functions(self):
        return {'package_review': _package_review}
    
    def _trace(self, context, data_dict=None):
        if context is not None:
            print "----context----"
            print [value for value in context.iteritems()]
        if data_dict is not None:
            print "----data_dict----"
            print [value for value in data_dict.iteritems()]
            pass
        if plugins.toolkit.c is not None:
            print "----plugins.toolkit.c----"
            print plugins.toolkit.c
            pass

   
@auth_sysadmins_check
def _package_review(context, data_dict=None):
    can_update = tk.check_access('package_update', context, data_dict)
    if can_update:
        package = logic_auth.get_package_object(context, data_dict)

        creator_user_id = converters.convert_user_name_or_id_to_id(tk.c.user, context)
        if package and (package.maintainer == tk.c.user or package.creator_user_id == creator_user_id):
            return {'success': True }
            
    return {'success': False, 'msg': 'Not allowed to update suspended packages'}
