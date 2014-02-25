import ckan.plugins as plugins
import ckan.lib.plugins as libplugins
import ckan.plugins.toolkit as tk
import ckan.logic.schema
import datetime
import ckanext.iarmetadata.plugin as plugins2
import ckan.lib.helpers as h

class ReviewPlugin(plugins.SingletonPlugin, libplugins.DefaultOrganizationForm):
    """
    Setup plugin
    """
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins2.IDatasetFormExtra)
    
    """
    IRoutes
    """
    def before_map(self, map):

        map.connect('review', '/review/{id}',
            controller='ckanext.review.controller:ReviewController',
            action='index')

        return map
    
    """
    IConfigurer
    """
    def update_config(self, config):
        plugins.toolkit.add_template_directory(config, 'templates')
    
    """
    IGroupForm
    """
    def is_fallback(self):
        return False
    
    def group_types(self):
        return ('organization',)
    
    def form_to_db_schema(self):
        schema = super(ReviewPlugin, self).form_to_db_schema()
        schema.update({
                'dataset_review_interval': [tk.get_validator('ignore_missing'), tk.get_validator('is_positive_integer'),
                    tk.get_converter('convert_to_extras')]
                })
        schema.update({
                'dataset_review_interval_type': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_extras')]
                })
        return schema
    
    def db_to_form_schema(self):
        schema = super(ReviewPlugin, self).db_to_form_schema()
        if not schema:
            schema = ckan.logic.schema.group_form_schema()
            #schema = ckan.logic.schema.default_group_schema()
            schema['num_followers'] = [tk.get_validator('ignore_missing')]
            schema['package_count'] = [tk.get_validator('ignore_missing')]
            schema.update({
                'dataset_review_interval': [tk.get_converter('convert_from_extras'),
                    tk.get_validator('ignore_missing'), tk.get_validator('is_positive_integer')]
                })
            schema.update({
                'dataset_review_interval_type': [tk.get_converter('convert_from_extras'),
                    tk.get_validator('ignore_missing')]
                })
        return schema
    
    def check_data_dict(self, data_dict):
        dataset_review_interval = data_dict.get('dataset_review_interval', None)
    
    def setup_template_variables(self, context, data_dict):
        super(ReviewPlugin, self).setup_template_variables(context, data_dict)
        
        tk.c.dataset_review_interval_types = ('day(s)', 'week(s)', 'month(s)', 'year(s)')
        
        
    """
    IDatasetFormExtra
    """
    def IDatasetFormExtra_create_package_schema(self, schema):
        schema.update({
        'next_review_timestamp': [tk.get_validator('ignore_missing'),
                             jsonisodate,
            tk.get_converter('convert_to_extras')]
        })
                
    def IDatasetFormExtra_update_package_schema(self, schema):
        schema.update({
        'next_review_timestamp': [tk.get_validator('ignore_missing'),
                             jsonisodate,
            tk.get_converter('convert_to_extras')]
        })

    def IDatasetFormExtra_show_package_schema(self, schema):
        schema.update({
        'next_review_timestamp': [tk.get_converter('convert_from_extras'),
            tk.get_validator('ignore_missing'),
            jsonisodate]
        })
       
    def IDatasetFormExtra_setup_template_variables(self, context, data_dict):
        #set the default review date value
        if ('owner_org' in data_dict):
            owner_context = { 'user': context['user'],'for_view': True, 'include_datasets' : False }
            
            owner_dict = { 'id' : data_dict['owner_org']}
            owner = tk.get_action('organization_show')(owner_context, owner_dict)
            review_date = datetime.date.today()
            
            if 'dataset_review_interval' in owner and 'dataset_review_interval_type' in owner:
                if owner['dataset_review_interval_type'] == "day(s)":
                    review_date = review_date + datetime.timedelta(days=owner['dataset_review_interval'])
                if owner['dataset_review_interval_type'] == "week(s)":
                    review_date = review_date + datetime.timedelta(weeks=owner['dataset_review_interval'])
                if owner['dataset_review_interval_type'] == "month(s)":
                    review_date = review_date + datetime.timedelta(months=owner['dataset_review_interval'])
                if owner['dataset_review_interval_type'] == "year(s)":
                    review_date = review_date + datetime.timedelta(years=owner['dataset_review_interval'])
                
                data_dict['next_review_timestamp'] = str(review_date)
    
    
"""
jsonisodate
"""   
def jsonisodate(value, context):
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if value == '':
        return None
    return h.date_str_to_datetime(value).date().isoformat()