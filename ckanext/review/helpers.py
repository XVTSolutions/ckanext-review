import datetime
import ckan.plugins.toolkit as tk

def calculate_next_review_date(context, owner_org):
    owner_context = { 'user': context['user'],'for_view': True, 'include_datasets' : False }
                
    owner_dict = { 'id' : owner_org}
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
        
    return review_date