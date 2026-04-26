from django.contrib import admin
from .models import IrregularVerb, GameSession


@admin.register(IrregularVerb)
class IrregularVerbAdmin(admin.ModelAdmin):
    list_display = ('base', 'past', 'pp', 'created_at')
    search_fields = ('base', 'past', 'pp')
    ordering = ('base',)


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'mode', 'correct', 'total', 'score_pct', 'played_at')
    list_filter = ('mode', 'played_at')
    search_fields = ('player_name',)
    readonly_fields = ('played_at',)
