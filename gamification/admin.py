from django.contrib import admin
from .models import (
    Player, VocabWord, Achievement, PlayerAchievement, GamePlaySession,
    GrammarTopic, GrammarQuestion, PlayerTopicProgress,
    SurvivalScenario, SurvivalNode, SurvivalChoice, PlayerSurvivalProgress,
    VBUnit, VBWord, VBQuestion, VBPassage, VBPassageQuestion, PlayerVBUnitProgress,
)


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


@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    list_display = ('order', 'icon', 'name', 'description')
    ordering = ('order',)


@admin.register(GrammarQuestion)
class GrammarQuestionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'question_type', 'prompt', 'correct_answer', 'is_boss')
    list_filter = ('topic', 'question_type', 'is_boss')
    search_fields = ('prompt',)


@admin.register(PlayerTopicProgress)
class PlayerTopicProgressAdmin(admin.ModelAdmin):
    list_display = ('player', 'topic', 'completed', 'best_score_pct', 'updated_at')
    list_filter = ('topic', 'completed')


@admin.register(SurvivalScenario)
class SurvivalScenarioAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'description')


@admin.register(SurvivalNode)
class SurvivalNodeAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'node_key', 'npc_line', 'is_start', 'is_ending', 'ending_quality')
    list_filter = ('scenario', 'is_start', 'is_ending')


@admin.register(SurvivalChoice)
class SurvivalChoiceAdmin(admin.ModelAdmin):
    list_display = ('node', 'choice_text', 'quality', 'next_node')
    list_filter = ('quality',)


@admin.register(PlayerSurvivalProgress)
class PlayerSurvivalProgressAdmin(admin.ModelAdmin):
    list_display = ('player', 'scenario', 'attempts_count', 'best_ending_quality', 'completed')
    list_filter = ('scenario', 'completed')


@admin.register(VBUnit)
class VBUnitAdmin(admin.ModelAdmin):
    list_display = ('order', 'icon', 'name', 'description')
    ordering = ('order',)


@admin.register(VBWord)
class VBWordAdmin(admin.ModelAdmin):
    list_display = ('unit', 'word', 'pronunciation', 'part_of_speech', 'definition')
    list_filter = ('unit',)
    search_fields = ('word', 'definition')


@admin.register(VBQuestion)
class VBQuestionAdmin(admin.ModelAdmin):
    list_display = ('unit', 'prompt', 'correct_answer')
    list_filter = ('unit',)
    search_fields = ('prompt',)


@admin.register(VBPassage)
class VBPassageAdmin(admin.ModelAdmin):
    list_display = ('unit', 'title')


@admin.register(VBPassageQuestion)
class VBPassageQuestionAdmin(admin.ModelAdmin):
    list_display = ('passage', 'prompt', 'correct_answer')
    search_fields = ('prompt',)


@admin.register(PlayerVBUnitProgress)
class PlayerVBUnitProgressAdmin(admin.ModelAdmin):
    list_display = ('player', 'unit', 'completed', 'best_score_pct', 'updated_at')
    list_filter = ('unit', 'completed')
