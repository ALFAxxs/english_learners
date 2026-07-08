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
        ('survival_scenarios_completed', 'Survival Scenarios Completed (Good Ending)'),
        ('vocab_units_completed', 'Vocabulary Builder Units Completed'),
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
        ('survival_challenge', 'Daily Survival Challenge'),
        ('vocabulary_builder', 'Vocabulary Builder'),
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


# ─── DAILY SURVIVAL CHALLENGE ───────────────────────────────────────────────

class SurvivalScenario(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, default='🧳')
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Survival Scenario"
        verbose_name_plural = "Survival Scenarios"

    def __str__(self):
        return f"{self.icon} {self.name}"


class SurvivalNode(models.Model):
    ENDING_QUALITY_CHOICES = [('good', 'Good'), ('neutral', 'Neutral'), ('bad', 'Bad')]

    scenario = models.ForeignKey(SurvivalScenario, on_delete=models.CASCADE, related_name='nodes')
    node_key = models.CharField(max_length=50)
    npc_line = models.CharField(max_length=300)
    is_start = models.BooleanField(default=False)
    is_ending = models.BooleanField(default=False)
    ending_quality = models.CharField(max_length=10, choices=ENDING_QUALITY_CHOICES, blank=True)

    class Meta:
        unique_together = ('scenario', 'node_key')
        ordering = ['scenario', 'node_key']
        verbose_name = "Survival Node"
        verbose_name_plural = "Survival Nodes"

    def __str__(self):
        return f"[{self.scenario.name}] {self.node_key}"


class SurvivalChoice(models.Model):
    QUALITY_CHOICES = [('good', 'Good'), ('ok', 'OK'), ('bad', 'Bad')]

    node = models.ForeignKey(SurvivalNode, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    feedback = models.CharField(max_length=300)
    next_node = models.ForeignKey(SurvivalNode, on_delete=models.CASCADE, related_name='reached_by')

    class Meta:
        ordering = ['node', 'id']
        verbose_name = "Survival Choice"
        verbose_name_plural = "Survival Choices"

    def __str__(self):
        return f"[{self.node}] {self.choice_text[:40]}"


class PlayerSurvivalProgress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='survival_progress')
    scenario = models.ForeignKey(SurvivalScenario, on_delete=models.CASCADE, related_name='player_progress')
    attempts_count = models.PositiveIntegerField(default=0)
    best_ending_quality = models.CharField(max_length=10, blank=True)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'scenario')
        verbose_name = "Player Survival Progress"
        verbose_name_plural = "Player Survival Progress"

    def __str__(self):
        return f"{self.player.name} – {self.scenario.name} ({self.best_ending_quality or 'not played'})"


# ─── VOCABULARY BUILDER ─────────────────────────────────────────────────────
# Note: named with a "VB" prefix (not "Vocab...") to avoid colliding with the
# pre-existing VocabWord model used by Word Hunter / Memory Cards.

class VBUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveSmallIntegerField()
    icon = models.CharField(max_length=10, default='📖')
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Vocabulary Builder Unit"
        verbose_name_plural = "Vocabulary Builder Units"

    def __str__(self):
        return f"{self.order}. {self.icon} {self.name}"


class VBWord(models.Model):
    unit = models.ForeignKey(VBUnit, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=50)
    pronunciation = models.CharField(max_length=60, blank=True)
    part_of_speech = models.CharField(max_length=12, blank=True)
    definition = models.CharField(max_length=300)
    example_sentence = models.CharField(max_length=300)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('unit', 'word')
        ordering = ['unit', 'order']
        verbose_name = "Vocabulary Builder Word"
        verbose_name_plural = "Vocabulary Builder Words"

    def __str__(self):
        return f"[{self.unit.name}] {self.word}"


class VBQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [('multiple_choice', 'Multiple Choice')]

    unit = models.ForeignKey(VBUnit, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    prompt = models.CharField(max_length=300)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=200)

    class Meta:
        ordering = ['unit', 'id']
        verbose_name = "Vocabulary Builder Question"
        verbose_name_plural = "Vocabulary Builder Questions"

    def __str__(self):
        return f"[{self.unit.name}] {self.prompt[:50]}"


class VBPassage(models.Model):
    unit = models.OneToOneField(VBUnit, on_delete=models.CASCADE, related_name='passage')
    title = models.CharField(max_length=100)
    body = models.TextField()

    class Meta:
        verbose_name = "Vocabulary Builder Passage"
        verbose_name_plural = "Vocabulary Builder Passages"

    def __str__(self):
        return f"[{self.unit.name}] {self.title}"


class VBPassageQuestion(models.Model):
    passage = models.ForeignKey(VBPassage, on_delete=models.CASCADE, related_name='questions')
    prompt = models.CharField(max_length=300)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=200)

    class Meta:
        ordering = ['passage', 'id']
        verbose_name = "Vocabulary Builder Passage Question"
        verbose_name_plural = "Vocabulary Builder Passage Questions"

    def __str__(self):
        return f"[{self.passage.title}] {self.prompt[:50]}"


class PlayerVBUnitProgress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='vb_progress')
    unit = models.ForeignKey(VBUnit, on_delete=models.CASCADE, related_name='player_progress')
    completed = models.BooleanField(default=False)
    best_score_pct = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'unit')
        verbose_name = "Player Vocabulary Unit Progress"
        verbose_name_plural = "Player Vocabulary Unit Progress"

    def __str__(self):
        return f"{self.player.name} – {self.unit.name} ({'done' if self.completed else 'in progress'})"
