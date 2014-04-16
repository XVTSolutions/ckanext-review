from sqlalchemy import orm, Table, Column, ForeignKey, types, and_
import ckan
from ckan.model.meta import metadata
from ckan.model.types import make_uuid
import ckan.plugins.toolkit as tk
from validators import get_validator as vdoj_get_validator 

group_review_table = Table('group_review', metadata,
        Column('group_id', types.UnicodeText, ForeignKey('group.id'), primary_key=True),
        Column('dataset_review_interval', types.Integer),
        Column('dataset_review_interval_type', types.UnicodeText)
    )

package_review_table = Table('package_review', metadata,
        Column('package_id', types.UnicodeText, ForeignKey('package.id'), primary_key=True),
        Column('next_review_date', types.Date),
    )

class PackageReview(object):
    pass

class GroupReview(ckan.model.domain_object.DomainObject):
    def validate(self):
        data = self.as_dict()
        errors = { 'dataset_review_interval' : [] }
        context = {}
        is_valid = True
        
#         validator = tk.get_validator('not_empty')
#         try:
#             validator('dataset_review_interval', data, errors, context)
#         except ckan.lib.navl.dictization_functions.StopOnError:
#             is_valid = False
           
        validator = vdoj_get_validator('in_range_date_positive_integer') 
        try:
            #validator('dataset_review_interval', data, errors, context)
            validator(data.get('dataset_review_interval', 0), context)
        except ckan.lib.navl.dictization_functions.Invalid as ie:
            is_valid = False
            errors['dataset_review_interval'].append(ie.error)
        
        return is_valid, errors

orm.mapper(GroupReview, group_review_table)

orm.mapper(PackageReview, package_review_table)

def create_table():
    package_review_table.create(checkfirst=True)
    group_review_table.create(checkfirst=True)
    
def get_by_date(session, date):
    return session.query(PackageReview).filter(PackageReview.next_review_date == date)

def get_by_daterange(session, startdate, enddate):
    return session.query(PackageReview).filter(
        and_(PackageReview.next_review_date >= startdate, PackageReview.next_review_date <= enddate)
    ).all()

def get_package_review(session, package_id):
    return session.query(PackageReview).filter(PackageReview.package_id == package_id).first()

def add_package_review(session, package_id, next_review_date):
    model = PackageReview()
    
    model.package_id = package_id
    model.next_review_date = next_review_date
    
    session.add(model)
    
    session.flush()
    
def update_package_review(session, package_review):
    session.query(PackageReview).filter(PackageReview.package_id == package_review.package_id).update({"next_review_date": package_review.next_review_date})
    session.refresh(package_review)
    
