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