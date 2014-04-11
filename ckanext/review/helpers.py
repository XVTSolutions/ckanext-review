import datetime
import ckan
import ckan.plugins.toolkit as tk
from dateutil.relativedelta import relativedelta
from model import GroupReview

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

