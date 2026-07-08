from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.hub, name='hub'),
    path('games/verbquest/',     views.index,           name='index'),
    path('games/word-hunter/',   views.word_hunter,     name='word_hunter'),
    path('games/memory-cards/',  views.memory_cards,    name='memory_cards'),
    path('games/grammar-battle/', views.grammar_battle, name='grammar_battle'),
    path('games/survival-challenge/', views.survival_challenge, name='survival_challenge'),
    path('games/vocabulary-builder/', views.vocabulary_builder, name='vocabulary_builder'),
    path('leaderboard/',         views.leaderboard_page, name='leaderboard_page'),

    # API
    path('api/verbs/',          views.api_verbs,          name='api_verbs'),
    path('api/save-session/',   views.api_save_session,   name='api_save_session'),
    path('api/save-snapshot/',  views.api_save_snapshot,  name='api_save_snapshot'),

    # Admin panel
    path('admin-panel/login/',                          views.admin_login_view,        name='admin_login'),
    path('admin-panel/logout/',                         views.admin_logout_view,       name='admin_logout'),
    path('admin-panel/',                                views.admin_dashboard,         name='admin_dashboard'),
    path('admin-panel/stats/',                          views.admin_stats,             name='admin_stats'),
    path('admin-panel/verbs/',                          views.admin_verbs,             name='admin_verbs'),
    path('admin-panel/sessions/',                       views.admin_sessions,          name='admin_sessions'),
    path('admin-panel/game-sessions/',                  views.admin_game_sessions,     name='admin_game_sessions'),
    path('admin-panel/sessions/<int:pk>/delete/',       views.admin_delete_session,    name='admin_delete_session'),
    path('admin-panel/sessions/<int:pk>/snapshots/',    views.admin_session_snapshots, name='admin_session_snapshots'),
]