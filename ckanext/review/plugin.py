import ckan.plugins as plugins
import ckan.lib.plugins as libplugins
import ckan.plugins.toolkit as tk
import ckan.logic.schema
import datetime

class ReviewPlugin(plugins.SingletonPlugin, libplugins.DefaultOrganizationForm):
    """
    Setup plugin
    """
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IMapper)
    
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
                'dataset_review_interval': [tk.get_validator('ignore_missing'),
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
                    tk.get_validator('ignore_missing')]
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
        
        
        
    def before_insert(self, mapper, connection, instance):
        #if type(instance) is ckan.model.package.Package and instance.type == "dataset":
        #    instance.extras["review_timestamp"] = datetime.datetime.now()
        pass
              
    def before_update(self, mapper, connection, instance):
        if type(instance) is ckan.model.package.Package and instance.type == "dataset":
            instance.extras["review_timestamp"] = datetime.datetime.now()
        #pass

    def before_delete(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        pass