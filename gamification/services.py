import math
from datetime import timedelta

from django.utils import timezone

from .models import Player, Achievement, PlayerAchievement, GamePlaySession

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
        'unlocked_achievements': list(
            PlayerAchievement.objects.filter(player=player).values_list('achievement__code', flat=True)
        ),
    }
