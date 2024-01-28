from django.urls import path
from . import views

app_name = 'myself'

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('observation/', views.observation_view, name='observation_view'),
    path('situation/', views.situation_view, name='situation_view'),
    path('add_observation/', views.add_observation, name='add_observation'),
    path('get_observation/', views.get_observation, name='get_observation'),
    path('get_choice/', views.get_choice, name='get_choice'),
    path('stats_Activities/', views.stats_view_activities, name='stats_view_activities'),
    path('stats_Objects/', views.stats_view_objects, name='stats_view_objects'),
    path('stats_Contexts/', views.stats_view_contexts, name='stats_view_contexts'),
    path('stats_Bridges/', views.stats_view_emotional_bridge, name='stats_view_emotional_bridge'),
    path('remove_log/<int:log_id>/<str:target>/', views.remove_log, name='stats_view_emotional_bridge'),

]
