from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_info, name='api_info'),
    path('register', views.register_customer, name='register_customer'),
    path('check-eligibility', views.check_loan_eligibility, name='check_loan_eligibility'),
    path('create-loan', views.create_loan, name='create_loan'),
    path('view-loan/<uuid:loan_id>', views.view_loan, name='view_loan'),
    path('view-loans/<uuid:customer_id>', views.view_loans_by_customer, name='view_loans_by_customer'),
]