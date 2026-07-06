from django.contrib import admin
from .models import Player, VocabWord, Achievement, PlayerAchievement, GamePlaySession


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'xp', 'coins', 'current_streak', 'longest_streak', 'created_at')
    search_fields = ('name', 'uuid')
    list_filter = ('level',)


@admin.register(VocabWord)
class VocabWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'meaning', 'category', 'difficulty')
    list_filter = ('category', 'difficulty')
    search_fields = ('word', 'meaning')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('icon', 'title', 'condition_type', 'condition_value', 'xp_reward', 'coin_reward')
    list_filter = ('condition_type',)


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ('player', 'achievement', 'unlocked_at')
    list_filter = ('achievement',)


@admin.register(GamePlaySession)
class GamePlaySessionAdmin(admin.ModelAdmin):
    list_display = ('player', 'game_type', 'score', 'xp_earned', 'coins_earned', 'played_at')
    list_filter = ('game_type',)
    search_fields = ('player__name',)
