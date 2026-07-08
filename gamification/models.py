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
        ('grammar_topics_completed', 'Grammar Topics Completed'),
        ('boss_rounds_cleared', 'Grammar Boss Rounds Cleared'),
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
        ('grammar_battle', 'Grammar Battle'),
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


# ─── GRAMMAR BATTLE ─────────────────────────────────────────────────────────

class GrammarTopic(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(unique=True)
    icon = models.CharField(max_length=10, default='📘')
    description = models.CharField(max_length=200, blank=True)
    lesson_rule = models.TextField(blank=True)
    lesson_structure = models.TextField(blank=True)
    lesson_signal_words = models.JSONField(default=list, blank=True)
    lesson_examples = models.JSONField(default=list, blank=True)
    lesson_common_mistakes = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Grammar Topic"
        verbose_name_plural = "Grammar Topics"

    def __str__(self):
        return f"{self.order}. {self.icon} {self.name}"


class GrammarQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('fill_blank', 'Fill In The Blank'),
        ('drag_drop', 'Drag And Drop (Word Order)'),
    ]

    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    prompt = models.CharField(max_length=300)
    options = models.JSONField(default=list, blank=True)
    correct_answer = models.CharField(max_length=200)
    is_boss = models.BooleanField(default=False)

    class Meta:
        ordering = ['topic', 'id']
        verbose_name = "Grammar Question"
        verbose_name_plural = "Grammar Questions"

    def __str__(self):
        return f"[{self.topic.name}] {self.prompt[:50]}"


class PlayerTopicProgress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='topic_progress')
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='player_progress')
    completed = models.BooleanField(default=False)
    best_score_pct = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'topic')
        verbose_name = "Player Topic Progress"
        verbose_name_plural = "Player Topic Progress"

    def __str__(self):
        return f"{self.player.name} – {self.topic.name} ({'done' if self.completed else 'in progress'})"
