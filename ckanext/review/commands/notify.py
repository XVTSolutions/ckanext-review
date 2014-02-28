import sys
from ckan.lib.cli import CkanCommand
from ckanext.review.model import get_by_date
import ckan
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import datetime
from ckan.logic.validators import object_id_validators

class NotifyCommand(CkanCommand):
    '''
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def __init__(self,name):
        super(NotifyCommand,self).__init__(name)


    def command(self):
        self._load_config()
        
        object_id_validators['review package'] = tk.get_validator('package_id_exists')
#         if len(self.args) == 0:
#             self.parser.print_usage()
#             sys.exit(1)

        context = {'model': ckan.model,
           'session': ckan.model.Session,
           'ignore_auth': True}

        #get all packages that need to be reviewed today
        package_reviews = get_by_date(ckan.model.Session, datetime.date.today())
        
        for pr in package_reviews:
            #get the package
            pkg = ckan.model.Package.get(pr.package_id)
            pkg_dict = ckan.lib.dictization.table_dictize(pkg, context)
            
            #add item into the creators activity stream indicating the package needs to be reviewed
            activity_dict = {
                'user_id': pkg.creator_user_id,
                'object_id': pr.package_id,
                'data' : { 'dataset': pkg_dict },
                'activity_type': 'review package',
            }
            plugins.toolkit.get_action('activity_create')(context, activity_dict)    
        