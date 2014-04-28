import datetime
import ckan
import ckan.plugins.toolkit as tk
from dateutil.relativedelta import relativedelta
from model import GroupReview
from ckan.model import Activity, ActivityDetail
#from ckan.lib.email_notifications import _notifications_functions
from ckan.lib.activity_streams import activity_stream_string_functions, activity_stream_string_icons

dataset_activity_type_package_reviewed = 'package reviewed'
dataset_activity_type_review_package = 'review package'

def get_dataset_review_interval_types():
    return ('day(s)', 'week(s)', 'month(s)', 'year(s)')

def calculate_next_review_date(context, owner_org):
    
    gr = ckan.model.Session.query(GroupReview).filter(GroupReview.group_id == owner_org).first()
    review_date = datetime.date.today()
    
    if gr is not None:
        if gr.dataset_review_interval_type == "day(s)":
            review_date = review_date + datetime.timedelta(days=gr.dataset_review_interval)
        if gr.dataset_review_interval_type == "week(s)":
            review_date = review_date + datetime.timedelta(weeks=gr.dataset_review_interval)
        if gr.dataset_review_interval_type == "month(s)":
            review_date = review_date + relativedelta(months=gr.dataset_review_interval)
        if gr.dataset_review_interval_type == "year(s)":
            review_date = review_date + relativedelta(years=gr.dataset_review_interval)
        
    return review_date

def ckanext_review_get_next_review_date(data):
    org_id = _get_org_id(data)
    
    if org_id is not None:
        review_date = calculate_next_review_date(None, org_id)
        au_date = datetime.datetime.strftime(review_date, '%d-%m-%Y')
        return au_date

def _get_org_id(data):
    org_id = None
    
    if tk.request.method == "POST" and tk.request.POST.has_key("owner_org"):
        #when editing a dataset and the organisation is changed, set the org_id to the newly selected org
        org_id = tk.request.POST.get("owner_org", None)
    elif data is not None and data.has_key('group_id') and data['group_id'] is not None:
        #when creating new dataset, can get organization_id from group_id
        org_id = data['group_id']
    elif data is not None and data.has_key('organization') and data['organization'] is not None:
        #when updating the dataset, can get organization_id from organization.id
        organization = data["organization"]
        if organization and organization.has_key('is_organization') and organization['is_organization'] and organization.has_key('id'):
            org_id = organization['id']
    elif data is not None and data.has_key('owner_org') and data['owner_org'] is not None:
        #when creating new dataset that is not valid, can get organization_id from owner_org
        org_id = data['owner_org']
        
    #make sure owner_org is the same value
    if 'owner_org' in data and data['owner_org'] != org_id:
        data['owner_org'] = org_id
    if 'group_id' in data and data['group_id'] != org_id:
        data['group_id'] = org_id  
        
    #make sure extras are loaded properly
    if 'extras' in data:
        for e in data['extras']:
            data[e['key']] = e['value']
    
    if org_id is not None and len(org_id) > 0:
        return org_id
    
    return None

def create_review_activity(context, pkg_dict, dataset_activity_type):

    model = context['model']
    user = context['user']
    userobj = model.User.get(user)
    detail_type_reviewed = 'reviewed'
    object_type_package = 'package'

    activity_object_id = pkg_dict.get('id')

    #create activity record
    activity = Activity(user_id=userobj.id, object_id=activity_object_id, revision_id=pkg_dict.get('revision_id'), activity_type=dataset_activity_type, data={object_type_package: pkg_dict,})
    activity.save()

    #create detail record
    activity_detail = ActivityDetail(activity_id=activity.id, object_id=activity.object_id, object_type=object_type_package, activity_type=detail_type_reviewed, data={object_type_package: pkg_dict,})
    activity_detail.save()

def register_activity_types():
    #_notifications_functions.append(notifications)
    activity_stream_string_functions[dataset_activity_type_package_reviewed] = activity_stream_string_package_reviewed
    activity_stream_string_functions[dataset_activity_type_review_package] = activity_stream_string_review_package
    activity_stream_string_icons[dataset_activity_type_review_package] = 'calendar'

def activity_stream_string_review_package(context, activity):
    return tk._("{dataset} is due for review")

def activity_stream_string_package_reviewed(context, activity):
    return tk._("{dataset} has been reviewed")

