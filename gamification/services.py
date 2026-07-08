import math
import re
from datetime import timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from .models import (
    Player, Achievement, PlayerAchievement, GamePlaySession,
    GrammarTopic, PlayerTopicProgress,
    SurvivalScenario, PlayerSurvivalProgress,
    VBUnit, PlayerVBUnitProgress,
)

GRAMMAR_PASS_THRESHOLD = 0.7  # correct/total ratio needed to unlock the next topic
VB_PASS_THRESHOLD = 0.7  # correct/total ratio needed to unlock the next vocabulary unit

DAILY_REWARD_CYCLE = [20, 30, 40, 60, 80, 100, 150]  # coins, indexed by (streak - 1) % 7


def xp_to_level(xp):
    """level = floor(sqrt(xp / 50)) + 1"""
    return int(math.sqrt(xp / 50)) + 1


def xp_for_next_level(level):
    return 50 * (level ** 2)


def get_or_create_player(uuid, name=None):
    player, created = Player.objects.get_or_create(
        uuid=uuid,
        defaults={'name': (name or 'Player').strip()[:100] or 'Player'},
    )
    if not created and name and name.strip() and player.name != name.strip():
        player.name = name.strip()[:100]
        player.save(update_fields=['name'])
    return player


# ─── ACCOUNT RECOVERY (phone + password) ───────────────────────────────────

def normalize_phone(raw):
    if not raw:
        return ''
    digits = re.sub(r'[^\d+]', '', raw.strip())
    if digits.startswith('+'):
        return digits
    if digits.startswith('998') and len(digits) == 12:
        return '+' + digits
    if len(digits) == 9:
        return '+998' + digits
    return digits


def link_account(player, phone, raw_password):
    """Attach phone+password to this player. Returns (ok, error)."""
    phone = normalize_phone(phone)
    if len(phone) < 9:
        return False, "Telefon raqam noto'g'ri."
    if not raw_password or len(raw_password) < 6:
        return False, "Parol kamida 6 ta belgidan iborat bo'lishi kerak."

    existing = Player.objects.filter(phone=phone).exclude(pk=player.pk).first()
    if existing:
        return False, "Bu raqam allaqachon ro'yxatdan o'tgan. Kirish orqali foydalaning."

    player.phone = phone
    player.password_hash = make_password(raw_password)
    player.save(update_fields=['phone', 'password_hash'])
    return True, None


def authenticate_by_phone(phone, raw_password):
    """Returns the Player if phone+password match, else None."""
    phone = normalize_phone(phone)
    try:
        player = Player.objects.get(phone=phone)
    except Player.DoesNotExist:
        return None
    if not player.password_hash or not check_password(raw_password, player.password_hash):
        return None
    return player


def add_xp(player, amount):
    if amount <= 0:
        return False, player.level
    old_level = player.level
    player.xp += amount
    new_level = xp_to_level(player.xp)
    level_up = new_level > old_level
    player.level = new_level
    player.weekly_xp += amount
    player.save(update_fields=['xp', 'level', 'weekly_xp'])
    return level_up, new_level


def add_coins(player, amount):
    if amount <= 0:
        return
    player.coins += amount
    player.save(update_fields=['coins'])


def spend_coins(player, amount):
    if amount <= 0 or player.coins < amount:
        return False
    player.coins -= amount
    player.save(update_fields=['coins'])
    return True


def _roll_weekly_xp(player, today):
    if player.week_reset_date is None or (today - player.week_reset_date).days >= 7:
        player.weekly_xp = 0
        player.week_reset_date = today
        player.save(update_fields=['weekly_xp', 'week_reset_date'])


def update_streak(player):
    """Call once per completed game. Returns (streak, streak_broken, already_played_today)."""
    today = timezone.localdate()
    _roll_weekly_xp(player, today)

    if player.last_active_date == today:
        return player.current_streak, False, True

    streak_broken = False
    if player.last_active_date == today - timedelta(days=1):
        player.current_streak += 1
    else:
        streak_broken = player.last_active_date is not None
        player.current_streak = 1

    player.longest_streak = max(player.longest_streak, player.current_streak)
    player.last_active_date = today
    player.save(update_fields=['current_streak', 'longest_streak', 'last_active_date'])
    return player.current_streak, streak_broken, False


def claim_daily_reward(player):
    """One claim per calendar day. Returns (claimed, coins_awarded, xp_awarded, day_in_cycle)."""
    today = timezone.localdate()
    if player.last_daily_claim_date == today:
        return False, 0, 0, ((player.current_streak - 1) % 7) + 1 if player.current_streak else 1

    day_in_cycle = ((player.current_streak - 1) % 7) if player.current_streak > 0 else 0
    coins = DAILY_REWARD_CYCLE[day_in_cycle]
    xp = 10 + day_in_cycle * 5

    add_coins(player, coins)
    add_xp(player, xp)
    player.last_daily_claim_date = today
    player.save(update_fields=['last_daily_claim_date'])

    return True, coins, xp, day_in_cycle + 1


def xp_for_game(game_type, score_ratio, combo=0, duration_seconds=0):
    """score_ratio: 0..1 (correct/total or an equivalent normalized score)."""
    score_ratio = max(0.0, min(1.0, score_ratio))
    base = {
        'verbquest': 60,
        'word_hunter': 80,
        'memory_cards': 70,
        'grammar_battle': 80,
        'survival_challenge': 70,
        'vocabulary_builder': 85,
    }.get(game_type, 50)

    xp = base * score_ratio
    combo_bonus = min(combo, 20) * 1.5
    xp += combo_bonus

    if score_ratio >= 0.999:
        xp += base * 0.25  # perfect-score bonus

    return int(round(xp))


def coins_for_game(xp_earned):
    return max(1, int(round(xp_earned * 0.4)))


def check_achievements(player, context):
    """context: {'game_type', 'score_ratio', 'combo', 'words_found_total'(optional)}"""
    newly_unlocked = []
    unlocked_codes = set(
        PlayerAchievement.objects.filter(player=player).values_list('achievement__code', flat=True)
    )

    games_played = GamePlaySession.objects.filter(player=player).count()
    word_hunter_words_found = sum(
        s.meta.get('words_found', 0)
        for s in GamePlaySession.objects.filter(player=player, game_type='word_hunter')
    )
    boss_rounds_cleared = sum(
        1 for s in GamePlaySession.objects.filter(player=player, game_type='grammar_battle')
        if s.meta.get('boss_cleared')
    )
    stats = {
        'games_played': games_played,
        'streak': player.current_streak,
        'total_xp': player.xp,
        'coins_earned': player.coins,
        'combo': context.get('combo', 0),
        'game_perfect_score': 1 if context.get('score_ratio', 0) >= 0.999 else 0,
        'word_hunter_words_found': word_hunter_words_found,
        'memory_cards_completed': (
            GamePlaySession.objects.filter(player=player, game_type='memory_cards').count()
        ),
        'grammar_topics_completed': PlayerTopicProgress.objects.filter(player=player, completed=True).count(),
        'boss_rounds_cleared': boss_rounds_cleared,
        'survival_scenarios_completed': (
            PlayerSurvivalProgress.objects.filter(player=player, completed=True).count()
        ),
        'vocab_units_completed': (
            PlayerVBUnitProgress.objects.filter(player=player, completed=True).count()
        ),
    }

    for achievement in Achievement.objects.all():
        if achievement.code in unlocked_codes:
            continue
        value = stats.get(achievement.condition_type, 0)
        if value >= achievement.condition_value:
            PlayerAchievement.objects.create(player=player, achievement=achievement)
            if achievement.xp_reward:
                add_xp(player, achievement.xp_reward)
            if achievement.coin_reward:
                add_coins(player, achievement.coin_reward)
            newly_unlocked.append(achievement)

    return newly_unlocked


def player_profile(player):
    next_level_xp = xp_for_next_level(player.level)
    prev_level_xp = xp_for_next_level(player.level - 1) if player.level > 1 else 0
    progress = player.xp - prev_level_xp
    needed = max(1, next_level_xp - prev_level_xp)

    return {
        'uuid': player.uuid,
        'name': player.name,
        'xp': player.xp,
        'level': player.level,
        'level_progress_xp': progress,
        'level_needed_xp': needed,
        'coins': player.coins,
        'current_streak': player.current_streak,
        'longest_streak': player.longest_streak,
        'weekly_xp': player.weekly_xp,
        'has_phone': bool(player.phone),
        'unlocked_achievements': list(
            PlayerAchievement.objects.filter(player=player).values_list('achievement__code', flat=True)
        ),
    }


# ─── GRAMMAR BATTLE ─────────────────────────────────────────────────────────

def get_topics_with_status(player):
    """Returns GrammarTopic list in order, each annotated with unlocked/completed/best_score_pct."""
    topics = list(GrammarTopic.objects.all())
    progress_by_topic = {
        p.topic_id: p
        for p in PlayerTopicProgress.objects.filter(player=player, topic__in=topics)
    }

    result = []
    previous_completed = True
    for topic in topics:
        progress = progress_by_topic.get(topic.id)
        completed = bool(progress and progress.completed)
        unlocked = previous_completed
        result.append({
            'id': topic.id,
            'name': topic.name,
            'icon': topic.icon,
            'description': topic.description,
            'order': topic.order,
            'unlocked': unlocked,
            'completed': completed,
            'best_score_pct': progress.best_score_pct if progress else 0,
            'lesson_rule': topic.lesson_rule,
            'lesson_structure': topic.lesson_structure,
            'lesson_signal_words': topic.lesson_signal_words,
            'lesson_examples': topic.lesson_examples,
            'lesson_common_mistakes': topic.lesson_common_mistakes,
        })
        previous_completed = completed
    return result


def is_topic_unlocked(player, topic):
    """A topic is unlocked if it's the first, or the previous-order topic is completed."""
    if topic.order <= 1:
        return True
    previous = GrammarTopic.objects.filter(order=topic.order - 1).first()
    if not previous:
        return True
    return PlayerTopicProgress.objects.filter(player=player, topic=previous, completed=True).exists()


def record_topic_attempt(player, topic, score_pct):
    """Upserts PlayerTopicProgress; marks completed if score_pct clears the pass threshold."""
    progress, _ = PlayerTopicProgress.objects.get_or_create(player=player, topic=topic)
    progress.best_score_pct = max(progress.best_score_pct, score_pct)
    if score_pct >= GRAMMAR_PASS_THRESHOLD * 100:
        progress.completed = True
    progress.save()
    return progress


# ─── DAILY SURVIVAL CHALLENGE ───────────────────────────────────────────────

_ENDING_RANK = {'bad': 0, 'neutral': 1, 'good': 2}


def get_scenarios_with_status(player):
    """All scenarios are always unlocked; annotate with per-player completion state."""
    scenarios = list(SurvivalScenario.objects.all())
    progress_by_scenario = {
        p.scenario_id: p
        for p in PlayerSurvivalProgress.objects.filter(player=player, scenario__in=scenarios)
    }
    result = []
    for scenario in scenarios:
        progress = progress_by_scenario.get(scenario.id)
        result.append({
            'id': scenario.id,
            'name': scenario.name,
            'icon': scenario.icon,
            'description': scenario.description,
            'completed': bool(progress and progress.completed),
            'best_ending_quality': progress.best_ending_quality if progress else '',
            'attempts_count': progress.attempts_count if progress else 0,
        })
    return result


def record_survival_attempt(player, scenario, ending_quality):
    """Upserts PlayerSurvivalProgress; marks completed once a 'good' ending is reached."""
    progress, _ = PlayerSurvivalProgress.objects.get_or_create(player=player, scenario=scenario)
    progress.attempts_count += 1
    if not progress.best_ending_quality or (
        _ENDING_RANK.get(ending_quality, 0) > _ENDING_RANK.get(progress.best_ending_quality, 0)
    ):
        progress.best_ending_quality = ending_quality
    if ending_quality == 'good':
        progress.completed = True
    progress.save()
    return progress


# ─── VOCABULARY BUILDER ─────────────────────────────────────────────────────

def get_vb_units_with_status(player):
    """Returns VBUnit list in order, each annotated with unlocked/completed/best_score_pct."""
    units = list(VBUnit.objects.all())
    progress_by_unit = {
        p.unit_id: p
        for p in PlayerVBUnitProgress.objects.filter(player=player, unit__in=units)
    }

    result = []
    previous_completed = True
    for unit in units:
        progress = progress_by_unit.get(unit.id)
        completed = bool(progress and progress.completed)
        unlocked = previous_completed
        result.append({
            'id': unit.id,
            'name': unit.name,
            'icon': unit.icon,
            'description': unit.description,
            'order': unit.order,
            'unlocked': unlocked,
            'completed': completed,
            'best_score_pct': progress.best_score_pct if progress else 0,
            'word_count': unit.words.count(),
        })
        previous_completed = completed
    return result


def is_vb_unit_unlocked(player, unit):
    """A unit is unlocked if it's the first, or the previous-order unit is completed."""
    if unit.order <= 1:
        return True
    previous = VBUnit.objects.filter(order=unit.order - 1).first()
    if not previous:
        return True
    return PlayerVBUnitProgress.objects.filter(player=player, unit=previous, completed=True).exists()


def record_vb_unit_attempt(player, unit, score_pct):
    """Upserts PlayerVBUnitProgress; marks completed if score_pct clears the pass threshold."""
    progress, _ = PlayerVBUnitProgress.objects.get_or_create(player=player, unit=unit)
    progress.best_score_pct = max(progress.best_score_pct, score_pct)
    if score_pct >= VB_PASS_THRESHOLD * 100:
        progress.completed = True
    progress.save()
    return progress
