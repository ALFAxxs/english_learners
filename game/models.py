from django.db import models
import os


class IrregularVerb(models.Model):
    base = models.CharField(max_length=100, unique=True, verbose_name="Base Form")
    past = models.CharField(max_length=100, verbose_name="Past Simple")
    pp = models.CharField(max_length=100, verbose_name="Past Participle")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['base']
        verbose_name = "Irregular Verb"
        verbose_name_plural = "Irregular Verbs"

    def __str__(self):
        return f"{self.base} – {self.past} – {self.pp}"


class GameSession(models.Model):
    MODE_CHOICES = [
        ('past', 'Past Simple'),
        ('pp', 'Past Participle'),
        ('both', 'Both'),
    ]

    player_name = models.CharField(max_length=100, verbose_name="Player Name")
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='both')
    total = models.PositiveIntegerField(default=0, verbose_name="Total Questions")
    correct = models.PositiveIntegerField(default=0, verbose_name="Correct Answers")
    wrong = models.PositiveIntegerField(default=0, verbose_name="Wrong Answers")
    score_pct = models.PositiveIntegerField(default=0, verbose_name="Score (%)")
    played_at = models.DateTimeField(auto_now_add=True, verbose_name="Played At")

    class Meta:
        ordering = ['-played_at']
        verbose_name = "Game Session"
        verbose_name_plural = "Game Sessions"

    def __str__(self):
        return f"{self.player_name} – {self.score_pct}% – {self.played_at.strftime('%Y-%m-%d %H:%M')}"


def snapshot_upload_path(instance, filename):
    return f"snapshots/session_{instance.session.id}/{filename}"


class PlayerSnapshot(models.Model):
    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='snapshots',
        verbose_name="Session"
    )
    verb_index = models.PositiveIntegerField(verbose_name="Verb Number")
    verb_base = models.CharField(max_length=100, verbose_name="Verb (base form)")
    image = models.ImageField(upload_to=snapshot_upload_path, verbose_name="Snapshot")
    taken_at = models.DateTimeField(auto_now_add=True, verbose_name="Taken At")

    class Meta:
        ordering = ['verb_index']
        verbose_name = "Player Snapshot"
        verbose_name_plural = "Player Snapshots"

    def __str__(self):
        return f"{self.session.player_name} – verb #{self.verb_index} ({self.verb_base})"