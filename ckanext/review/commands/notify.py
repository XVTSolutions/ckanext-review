import sys
from ckan.lib.cli import CkanCommand
from ckanext.review.model import get_by_daterange
import ckan
import pylons
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan.logic import get_action, NotFound
import datetime
import ckanext.review.helpers as h
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
        h.register_activity_types()

        object_id_validators[h.dataset_activity_type_review_package] = tk.get_validator('user_id_exists')#tk.get_validator('package_id_exists')
#         if len(self.args) == 0:
#             self.parser.print_usage()
#             sys.exit(1)

        context = {'model': ckan.model,
           'session': ckan.model.Session,
           'ignore_auth': True}
        
        admin_user = plugins.toolkit.get_action('get_site_user')(context,{})

        #get all packages that need to be reviewed
        package_reviews = get_by_daterange(ckan.model.Session, datetime.date(2001,1,1), datetime.date.today())

        for pr in package_reviews:
            #get the package
            pkg = ckan.model.Package.get(pr.package_id)
            pkg_dict = ckan.lib.dictization.table_dictize(pkg, context)
            if 'maintainer' in pkg_dict:
                recipient = pkg_dict.get('maintainer')
            elif 'creator_user_id' in pkg_dict:
                recipient = pkg_dict.get('creator_user_id')
            else:
                raise ValueError('User not found')

            # Check if user exists
            try:
                user = ckan.model.User.get(recipient)

                review_context = {
                    'model': ckan.model,
                    'user':user.name,
                    'session': ckan.model.Session,
                    'ignore_auth': True
                }

                h.create_review_activity(review_context, pkg_dict, h.dataset_activity_type_review_package)
            except NotFound:
#                raise ValueError('User not found')
                print 'User not found %s '%(recipient)
        print 'done'
        
