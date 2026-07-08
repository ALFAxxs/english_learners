import json
import random

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from .models import (
    Player, VocabWord, Achievement, GamePlaySession, GrammarTopic, GrammarQuestion,
    SurvivalScenario, SurvivalNode, SurvivalChoice,
    VBUnit, VBWord, VBQuestion, VBPassage,
)
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


# ─── GRAMMAR BATTLE ─────────────────────────────────────────────────────────

@require_GET
def grammar_topics_view(request):
    uuid = request.GET.get('uuid', '')
    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    return JsonResponse({'ok': True, 'topics': services.get_topics_with_status(player)})


@require_GET
def grammar_questions_view(request):
    uuid = request.GET.get('uuid', '')
    topic_id = request.GET.get('topic_id')
    count = min(20, int(request.GET.get('count', 10)))

    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    try:
        topic = GrammarTopic.objects.get(pk=topic_id)
    except (GrammarTopic.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'topic not found'}, status=404)

    if not services.is_topic_unlocked(player, topic):
        return JsonResponse({'ok': False, 'error': 'topic is locked'}, status=403)

    normal_qs = list(GrammarQuestion.objects.filter(topic=topic, is_boss=False))
    boss_qs = list(GrammarQuestion.objects.filter(topic=topic, is_boss=True))
    random.shuffle(normal_qs)
    random.shuffle(boss_qs)

    round_questions = normal_qs[:count - 1]
    if boss_qs:
        round_questions.append(boss_qs[0])
    elif normal_qs[count - 1:count]:
        round_questions.append(normal_qs[count - 1])

    return JsonResponse({
        'ok': True,
        'topic': {'id': topic.id, 'name': topic.name, 'icon': topic.icon},
        'questions': [
            {
                'id': q.id, 'question_type': q.question_type, 'prompt': q.prompt,
                'options': q.options, 'correct_answer': q.correct_answer, 'is_boss': q.is_boss,
            }
            for q in round_questions
        ],
    })


@require_POST
def grammar_complete(request):
    data = _json_body(request)
    player = _require_player(data)
    if not player:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    try:
        topic = GrammarTopic.objects.get(pk=data.get('topic_id'))
    except (GrammarTopic.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'topic not found'}, status=404)

    total = max(1, int(data.get('total', 1)))
    correct = max(0, int(data.get('correct', 0)))
    combo = int(data.get('combo', 0))
    duration_seconds = int(data.get('duration_seconds', 0))
    boss_cleared = bool(data.get('boss_cleared'))
    score_ratio = min(1.0, correct / total)
    score_pct = round(score_ratio * 100)

    xp_earned = services.xp_for_game('grammar_battle', score_ratio, combo, duration_seconds)
    if boss_cleared:
        xp_earned += 25
    coins_earned = services.coins_for_game(xp_earned)

    level_up, new_level = services.add_xp(player, xp_earned)
    services.add_coins(player, coins_earned)
    streak, streak_broken, _ = services.update_streak(player)

    progress = services.record_topic_attempt(player, topic, score_pct)

    GamePlaySession.objects.create(
        player=player, game_type='grammar_battle', score=correct,
        xp_earned=xp_earned, coins_earned=coins_earned, duration_seconds=duration_seconds,
        meta={'topic_id': topic.id, 'topic_name': topic.name, 'boss_cleared': boss_cleared},
    )

    new_achievements = services.check_achievements(player, {
        'game_type': 'grammar_battle', 'score_ratio': score_ratio, 'combo': combo,
    })
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
        'topic_completed': progress.completed,
        'new_achievements': [
            {'code': a.code, 'title': a.title, 'icon': a.icon, 'description': a.description,
             'xp_reward': a.xp_reward, 'coin_reward': a.coin_reward}
            for a in new_achievements
        ],
        'profile': services.player_profile(player),
    })


# ─── DAILY SURVIVAL CHALLENGE ───────────────────────────────────────────────

def _serialize_node(node):
    """Choices are text-only — quality/feedback are revealed only after the player picks one."""
    return {
        'node_id': node.id,
        'npc_line': node.npc_line,
        'is_ending': node.is_ending,
        'ending_quality': node.ending_quality if node.is_ending else None,
        'choices': [
            {'id': c.id, 'text': c.choice_text}
            for c in node.choices.all()
        ] if not node.is_ending else [],
    }


@require_GET
def survival_scenarios_view(request):
    uuid = request.GET.get('uuid', '')
    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    return JsonResponse({'ok': True, 'scenarios': services.get_scenarios_with_status(player)})


@require_GET
def survival_start_view(request):
    scenario_id = request.GET.get('scenario_id')
    try:
        scenario = SurvivalScenario.objects.get(pk=scenario_id)
    except (SurvivalScenario.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'scenario not found'}, status=404)

    start_node = scenario.nodes.filter(is_start=True).first()
    if not start_node:
        return JsonResponse({'ok': False, 'error': 'scenario has no start node'}, status=500)

    return JsonResponse({
        'ok': True,
        'scenario': {'id': scenario.id, 'name': scenario.name, 'icon': scenario.icon},
        'node': _serialize_node(start_node),
    })


@require_POST
def survival_choose_view(request):
    data = _json_body(request)
    try:
        choice = SurvivalChoice.objects.select_related('next_node').get(pk=data.get('choice_id'))
    except (SurvivalChoice.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'choice not found'}, status=404)

    return JsonResponse({
        'ok': True,
        'feedback': choice.feedback,
        'quality': choice.quality,
        'next_node': _serialize_node(choice.next_node),
    })


@require_POST
def survival_complete(request):
    data = _json_body(request)
    player = _require_player(data)
    if not player:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    try:
        scenario = SurvivalScenario.objects.get(pk=data.get('scenario_id'))
    except (SurvivalScenario.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'scenario not found'}, status=404)

    good_count = max(0, int(data.get('good_count', 0)))
    ok_count = max(0, int(data.get('ok_count', 0)))
    bad_count = max(0, int(data.get('bad_count', 0)))
    total_choices = max(1, int(data.get('total_choices', 1)))
    ending_quality = data.get('ending_quality') or 'neutral'
    duration_seconds = int(data.get('duration_seconds', 0))

    score_ratio = min(1.0, (good_count * 2 + ok_count) / (total_choices * 2))

    xp_earned = services.xp_for_game('survival_challenge', score_ratio, 0, duration_seconds)
    if ending_quality == 'good':
        xp_earned += 20
    coins_earned = services.coins_for_game(xp_earned)

    level_up, new_level = services.add_xp(player, xp_earned)
    services.add_coins(player, coins_earned)
    streak, streak_broken, _ = services.update_streak(player)

    services.record_survival_attempt(player, scenario, ending_quality)

    GamePlaySession.objects.create(
        player=player, game_type='survival_challenge', score=good_count,
        xp_earned=xp_earned, coins_earned=coins_earned, duration_seconds=duration_seconds,
        meta={
            'scenario_id': scenario.id, 'scenario_name': scenario.name,
            'ending_quality': ending_quality, 'good_count': good_count,
            'ok_count': ok_count, 'bad_count': bad_count,
        },
    )

    new_achievements = services.check_achievements(player, {
        'game_type': 'survival_challenge', 'score_ratio': score_ratio, 'combo': 0,
    })
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


# ─── VOCABULARY BUILDER ─────────────────────────────────────────────────────

@require_GET
def vb_units_view(request):
    uuid = request.GET.get('uuid', '')
    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    return JsonResponse({'ok': True, 'units': services.get_vb_units_with_status(player)})


@require_GET
def vb_unit_detail_view(request):
    uuid = request.GET.get('uuid', '')
    unit_id = request.GET.get('unit_id')

    try:
        player = Player.objects.get(uuid=uuid)
    except Player.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    try:
        unit = VBUnit.objects.get(pk=unit_id)
    except (VBUnit.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'unit not found'}, status=404)

    if not services.is_vb_unit_unlocked(player, unit):
        return JsonResponse({'ok': False, 'error': 'unit is locked'}, status=403)

    words = VBWord.objects.filter(unit=unit)
    questions = VBQuestion.objects.filter(unit=unit)
    passage = VBPassage.objects.filter(unit=unit).first()

    return JsonResponse({
        'ok': True,
        'unit': {'id': unit.id, 'name': unit.name, 'icon': unit.icon, 'description': unit.description},
        'words': [
            {
                'word': w.word, 'pronunciation': w.pronunciation,
                'part_of_speech': w.part_of_speech, 'definition': w.definition,
                'example_sentence': w.example_sentence,
            }
            for w in words
        ],
        'questions': [
            {'id': q.id, 'prompt': q.prompt, 'options': q.options, 'correct_answer': q.correct_answer}
            for q in questions
        ],
        'passage': {
            'title': passage.title if passage else '',
            'body': passage.body if passage else '',
            'questions': [
                {'id': pq.id, 'prompt': pq.prompt, 'options': pq.options, 'correct_answer': pq.correct_answer}
                for pq in (passage.questions.all() if passage else [])
            ],
        },
    })


@require_POST
def vb_complete_view(request):
    data = _json_body(request)
    player = _require_player(data)
    if not player:
        return JsonResponse({'ok': False, 'error': 'player not found'}, status=404)

    try:
        unit = VBUnit.objects.get(pk=data.get('unit_id'))
    except (VBUnit.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'unit not found'}, status=404)

    total = max(1, int(data.get('total', 1)))
    correct = max(0, int(data.get('correct', 0)))
    duration_seconds = int(data.get('duration_seconds', 0))
    score_ratio = min(1.0, correct / total)
    score_pct = round(score_ratio * 100)

    xp_earned = services.xp_for_game('vocabulary_builder', score_ratio, 0, duration_seconds)
    coins_earned = services.coins_for_game(xp_earned)

    level_up, new_level = services.add_xp(player, xp_earned)
    services.add_coins(player, coins_earned)
    streak, streak_broken, _ = services.update_streak(player)

    progress = services.record_vb_unit_attempt(player, unit, score_pct)

    GamePlaySession.objects.create(
        player=player, game_type='vocabulary_builder', score=correct,
        xp_earned=xp_earned, coins_earned=coins_earned, duration_seconds=duration_seconds,
        meta={'unit_id': unit.id, 'unit_name': unit.name},
    )

    new_achievements = services.check_achievements(player, {
        'game_type': 'vocabulary_builder', 'score_ratio': score_ratio, 'combo': 0,
    })
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
        'unit_completed': progress.completed,
        'new_achievements': [
            {'code': a.code, 'title': a.title, 'icon': a.icon, 'description': a.description,
             'xp_reward': a.xp_reward, 'coin_reward': a.coin_reward}
            for a in new_achievements
        ],
        'profile': services.player_profile(player),
    })
