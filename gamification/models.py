from django.db import models


class Player(models.Model):
    uuid = models.CharField(max_length=36, unique=True, db_index=True)
    name = models.CharField(max_length=100, default='Player')

    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=128, null=True, blank=True)

    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    coins = models.PositiveIntegerField(default=0)

    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    weekly_xp = models.PositiveIntegerField(default=0)
    week_reset_date = models.DateField(null=True, blank=True)
    last_daily_claim_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-xp']
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self):
        return f"{self.name} (Lv.{self.level}, {self.xp} XP)"


class VocabWord(models.Model):
    CATEGORY_CHOICES = [
        ('travel', 'Travel'),
        ('food', 'Food & Dining'),
        ('work', 'Work & Business'),
        ('daily', 'Daily Life'),
        ('health', 'Health'),
        ('nature', 'Nature & Weather'),
    ]
    DIFFICULTY_CHOICES = [(1, 'Easy'), (2, 'Medium'), (3, 'Hard')]

    word = models.CharField(max_length=40, unique=True)
    meaning = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='daily')
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=1)

    class Meta:
        ordering = ['category', 'difficulty', 'word']
        verbose_name = "Vocabulary Word"
        verbose_name_plural = "Vocabulary Words"

    def __str__(self):
        return f"{self.word} — {self.meaning}"


class Achievement(models.Model):
    CONDITION_CHOICES = [
        ('games_played', 'Total Games Played'),
        ('streak', 'Streak Days Reached'),
        ('total_xp', 'Total XP Reached'),
        ('game_perfect_score', 'Perfect Score In A Game'),
        ('combo', 'Combo Reached'),
        ('coins_earned', 'Total Coins Earned'),
        ('word_hunter_words_found', 'Total Words Found In Word Hunter'),
        ('memory_cards_completed', 'Memory Cards Sessions Completed'),
    ]

    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=10, default='🏆')
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    condition_type = models.CharField(max_length=30, choices=CONDITION_CHOICES)
    condition_value = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['condition_type', 'condition_value']
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return f"{self.icon} {self.title}"


class PlayerAchievement(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='unlocked_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='unlocks')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'achievement')
        ordering = ['-unlocked_at']
        verbose_name = "Player Achievement"
        verbose_name_plural = "Player Achievements"

    def __str__(self):
        return f"{self.player.name} → {self.achievement.title}"


class GamePlaySession(models.Model):
    GAME_CHOICES = [
        ('verbquest', 'VerbQuest'),
        ('word_hunter', 'Word Hunter'),
        ('memory_cards', 'Memory Cards'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='play_sessions')
    game_type = models.CharField(max_length=30, choices=GAME_CHOICES)
    score = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    coins_earned = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    meta = models.JSONField(default=dict, blank=True)
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-played_at']
        verbose_name = "Game Play Session"
        verbose_name_plural = "Game Play Sessions"

    def __str__(self):
        return f"{self.player.name} – {self.get_game_type_display()} – {self.played_at.strftime('%Y-%m-%d %H:%M')}"
