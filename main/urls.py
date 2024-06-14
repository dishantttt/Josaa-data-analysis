from django.urls import path
from . import views
urlpatterns = [
    path('',views.dashboard),
    path('csv',views.upload_csv),
    path('csv',views.upload_csv),
    path('filter',views.filter,name='filter'),
    path('data',views.printdata,name = 'data'),
    path('dig-q1',views.dig_q1,name = 'dig_q1'),
    path('sid-q1',views.sid_q1,name = 'sid_q1'),
    path('sid-q2',views.sid_q2,name = 'sid_q2'),
    path('sid-q3',views.sid_q3,name = 'sid_q3'),
    path('mohit-q1',views.Moh_q1,name = 'Moh_q1'),
    path('mohit-q1exp/',views.Moh_q1exp,name = 'Moh_q1exp'),
    path('mohit-q1exp2/',views.Moh_q1exp2,name = 'Moh_q1exp2'),
    path('mohit-q2',views.branch_popularity,name = 'Moh_q2'),
    path('dev-q3',views.dev_q3,name = 'dev_q3'),
    path('dig-q2',views.dig_q2,name = 'dig_q2'),
    path('trendspecial', views.trendspecial, name='trendspecial'),
    path('trenddual', views.trenddual, name='trenddual')
]

