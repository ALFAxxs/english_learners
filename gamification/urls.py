from django.urls import path
from . import views

urlpatterns = [
    path('player/init/',                 views.player_init,         name='g_player_init'),
    path('player/<str:uuid>/',           views.player_profile_view, name='g_player_profile'),
    path('player/<str:uuid>/claim-daily/', views.claim_daily,       name='g_claim_daily'),
    path('account/register/',            views.account_register,   name='g_account_register'),
    path('account/login/',               views.account_login,      name='g_account_login'),
    path('game/complete/',               views.game_complete,       name='g_game_complete'),
    path('coins/spend/',                 views.spend_coins,         name='g_spend_coins'),
    path('leaderboard/',                 views.leaderboard,         name='g_leaderboard'),
    path('achievements/',                views.achievements_view,   name='g_achievements'),
    path('words/',                       views.words_view,          name='g_words'),
    path('grammar/topics/',              views.grammar_topics_view,   name='g_grammar_topics'),
    path('grammar/questions/',           views.grammar_questions_view, name='g_grammar_questions'),
    path('grammar/complete/',            views.grammar_complete,      name='g_grammar_complete'),
    path('survival/scenarios/',          views.survival_scenarios_view, name='g_survival_scenarios'),
    path('survival/start/',              views.survival_start_view,     name='g_survival_start'),
    path('survival/choose/',             views.survival_choose_view,    name='g_survival_choose'),
    path('survival/complete/',           views.survival_complete,       name='g_survival_complete'),
    path('vocab/units/',                 views.vb_units_view,        name='g_vb_units'),
    path('vocab/unit/',                  views.vb_unit_detail_view,  name='g_vb_unit_detail'),
    path('vocab/complete/',              views.vb_complete_view,     name='g_vb_complete'),
]
