import json
import random

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from .models import Player, VocabWord, Achievement, GamePlaySession
from . import services


def _json_body(request):
    try:
        return json.loads(request.body or b'{}')
    except (json.JSONDecodeError, TypeError):
        return {}


def _require_player(data):
    uuid = (data.get('uuid') or '').strip()
    if not uuid:
        return None
    try:
        return Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return None


# ─── PLAYER ─────────────────────────────────────────────────────────────────

@require_POST
def player_init(request):
    data = _json_body(request)
    uuid = (data.get('uuid') or '').strip()
    if not uuid:
        return JsonResponse({'ok': False, 'error': 'uuid required'}, status=400)

    player = services.get_or_create_player(uuid, data.get('name'))
    return JsonResponse({'ok': True, 'profile': services.player_profile(player)})


@require_GET
def player_profile_view(request, uuid):
    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)
    return JsonResponse({'ok': True, 'profile': services.player_profile(player)})


# ─── ACCOUNT RECOVERY ───────────────────────────────────────────────────────

@require_POST
def account_register(request):
    data = _json_body(request)
    player = _require_player(data)
    if not player:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    ok, error = services.link_account(player, data.get('phone', ''), data.get('password', ''))
    if not ok:
        return JsonResponse({'ok': False, 'error': error}, status=400)
    return JsonResponse({'ok': True, 'profile': services.player_profile(player)})


@require_POST
def account_login(request):
    data = _json_body(request)
    player = services.authenticate_by_phone(data.get('phone', ''), data.get('password', ''))
    if not player:
        return JsonResponse({'ok': False, 'error': "Noto'g'ri telefon raqam yoki parol."}, status=400)
    return JsonResponse({'ok': True, 'uuid': player.uuid, 'profile': services.player_profile(player)})


# ─── GAME COMPLETE (single integration point for every game) ──────────────

@require_POST
def game_complete(request):
    data = _json_body(request)
    player = _require_player(data)
    if not player:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    game_type = data.get('game_type')
    if game_type not in dict(GamePlaySession.GAME_CHOICES):
        return JsonResponse({'ok': False, 'error': 'invalid game_type'}, status=400)

    total = max(1, int(data.get('total', 1)))
    correct = max(0, int(data.get('correct', 0)))
    score = int(data.get('score', correct))
    combo = int(data.get('combo', 0))
    duration_seconds = int(data.get('duration_seconds', 0))
    meta = data.get('meta') or {}
    score_ratio = min(1.0, correct / total) if data.get('correct') is not None else min(1.0, score / total)

    xp_earned = services.xp_for_game(game_type, score_ratio, combo, duration_seconds)
    coins_earned = services.coins_for_game(xp_earned)

    level_up, new_level = services.add_xp(player, xp_earned)
    services.add_coins(player, coins_earned)
    streak, streak_broken, already_played_today = services.update_streak(player)

    GamePlaySession.objects.create(
        player=player, game_type=game_type, score=score,
        xp_earned=xp_earned, coins_earned=coins_earned,
        duration_seconds=duration_seconds, meta=meta,
    )

    achievement_context = {
        'game_type': game_type,
        'score_ratio': score_ratio,
        'combo': combo,
    }
    new_achievements = services.check_achievements(player, achievement_context)
    games_played = GamePlaySession.objects.filter(player=player).count()

    return JsonResponse({
        'ok': True,
        'xp_earned': xp_earned,
        'coins_earned': coins_earned,
        'level_up': level_up,
        'new_level': new_level,
        'streak': streak,
        'streak_broken': streak_broken,
        'games_played': games_played,
        'new_achievements': [
            {'code': a.code, 'title': a.title, 'icon': a.icon, 'description': a.description,
             'xp_reward': a.xp_reward, 'coin_reward': a.coin_reward}
            for a in new_achievements
        ],
        'profile': services.player_profile(player),
    })


# ─── DAILY REWARD ───────────────────────────────────────────────────────────

@require_POST
def claim_daily(request, uuid):
    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)

    claimed, coins, xp, day_in_cycle = services.claim_daily_reward(player)
    return JsonResponse({
        'ok': True, 'claimed': claimed, 'coins_awarded': coins, 'xp_awarded': xp,
        'day_in_cycle': day_in_cycle, 'profile': services.player_profile(player),
    })


# ─── COINS: SPEND (power-ups) ──────────────────────────────────────────────

@require_POST
def spend_coins(request):
    data = _json_body(request)
    player = _require_player(data)
    if not player:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    amount = int(data.get('amount', 0))
    ok = services.spend_coins(player, amount)
    return JsonResponse({'ok': ok, 'coins': player.coins})


# ─── LEADERBOARD ────────────────────────────────────────────────────────────

@require_GET
def leaderboard(request):
    scope = request.GET.get('scope', 'alltime')
    order_field = '-weekly_xp' if scope == 'weekly' else '-xp'
    players = Player.objects.order_by(order_field)[:20]
    return JsonResponse({
        'ok': True,
        'scope': scope,
        'players': [
            {
                'name': p.name, 'level': p.level,
                'xp': p.weekly_xp if scope == 'weekly' else p.xp,
                'current_streak': p.current_streak,
            }
            for p in players
        ],
    })


# ─── ACHIEVEMENTS ───────────────────────────────────────────────────────────

@require_GET
def achievements_view(request):
    uuid = request.GET.get('uuid', '')
    unlocked_codes = set()
    if uuid:
        try:
            player = Player.objects.get(uuid=uuid)
            unlocked_codes = set(
                player.unlocked_achievements.values_list('achievement__code', flat=True)
            )
        except Player.DoesNotExist:
            pass

    achievements = Achievement.objects.all()
    return JsonResponse({
        'ok': True,
        'achievements': [
            {
                'code': a.code, 'title': a.title, 'description': a.description,
                'icon': a.icon, 'xp_reward': a.xp_reward, 'coin_reward': a.coin_reward,
                'unlocked': a.code in unlocked_codes,
            }
            for a in achievements
        ],
    })


# ─── WORDS (Word Hunter / Memory Cards word bank) ──────────────────────────

@require_GET
def words_view(request):
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    count = min(200, int(request.GET.get('count', 20)))
    seed = request.GET.get('seed')

    qs = VocabWord.objects.all()
    if category:
        qs = qs.filter(category=category)
    if difficulty:
        qs = qs.filter(difficulty=difficulty)

    words = list(qs.values('word', 'meaning', 'category', 'difficulty'))
    rng = random.Random(seed) if seed else random.Random()
    rng.shuffle(words)

    return JsonResponse({'ok': True, 'words': words[:count]})
