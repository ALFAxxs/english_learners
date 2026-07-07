import json
import base64
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Avg, Sum, Count
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import IrregularVerb, GameSession, PlayerSnapshot, SiteSettings
from gamification.models import Player, GamePlaySession, PlayerAchievement


def is_staff(user):
    return user.is_authenticated and user.is_staff


# ─── ERROR HANDLERS ────────────────────────────────────────────────────────

def error_400(request, exception=None):
    return render(request, '400.html', status=400)

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)


# ─── MAIN APP ──────────────────────────────────────────────────────────────

def hub(request):
    return render(request, 'game/hub.html')


def index(request):
    return render(request, 'game/index.html')


def word_hunter(request):
    return render(request, 'game/word_hunter.html')


def memory_cards(request):
    return render(request, 'game/memory_cards.html')


def leaderboard_page(request):
    return render(request, 'game/leaderboard.html')


# ─── API: VERBS ────────────────────────────────────────────────────────────

def api_verbs(request):
    verbs = list(IrregularVerb.objects.values('id', 'base', 'past', 'pp'))
    settings = SiteSettings.get()
    return JsonResponse({
        'verbs': verbs,
        'camera_required': settings.camera_required,
    })


# ─── API: SAVE SESSION ─────────────────────────────────────────────────────

@require_POST
def api_save_session(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')

        # Update existing session if session_id provided
        if session_id:
            try:
                session = GameSession.objects.get(id=session_id)
                session.total     = data.get('total', session.total)
                session.correct   = data.get('correct', session.correct)
                session.wrong     = data.get('wrong', session.wrong)
                session.score_pct = data.get('pct', session.score_pct)
                session.save()
                return JsonResponse({'ok': True, 'id': session.id})
            except GameSession.DoesNotExist:
                pass

        session = GameSession.objects.create(
            player_name=data.get('name', 'Anonymous'),
            mode=data.get('mode', 'both'),
            total=data.get('total', 0),
            correct=data.get('correct', 0),
            wrong=data.get('wrong', 0),
            score_pct=data.get('pct', 0),
        )
        return JsonResponse({'ok': True, 'id': session.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ─── API: SAVE SNAPSHOT ────────────────────────────────────────────────────

@require_POST
def api_save_snapshot(request):
    try:
        data       = json.loads(request.body)
        session_id = data.get('session_id')
        verb_index = data.get('verb_index', 0)
        verb_base  = data.get('verb_base', '')
        image_data = data.get('image')

        if not image_data or not session_id:
            return JsonResponse({'ok': False, 'error': 'Missing data'}, status=400)

        session = GameSession.objects.get(id=session_id)

        if ',' in image_data:
            image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)
        snap = PlayerSnapshot(session=session, verb_index=verb_index, verb_base=verb_base)
        snap.image.save(f"verb_{verb_index}.jpg", ContentFile(image_bytes), save=True)

        return JsonResponse({'ok': True, 'id': snap.id})
    except GameSession.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ─── ADMIN PANEL ───────────────────────────────────────────────────────────

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', '')
        )
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        return render(request, 'admin_panel/login.html', {'error': True})
    return render(request, 'admin_panel/login.html', {'error': False})


def admin_logout_view(request):
    logout(request)
    return redirect('index')


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_dashboard(request):
    # Handle settings toggle
    if request.method == 'POST':
        s = SiteSettings.get()
        s.camera_required = request.POST.get('camera_required') == 'on'
        s.save()
        messages.success(request, 'Settings saved!')
        return redirect('admin_dashboard')

    site_settings = SiteSettings.get()
    context = {
        'total_verbs':     IrregularVerb.objects.count(),
        'total_sessions':  GameSession.objects.count(),
        'avg_score':       round(GameSession.objects.aggregate(avg=Avg('score_pct'))['avg'] or 0),
        'unique_players':  GameSession.objects.values('player_name').distinct().count(),
        'total_snapshots': PlayerSnapshot.objects.count(),
        'recent_sessions': GameSession.objects.all()[:10],
        'site_settings':   site_settings,
        'active_tab':      'dashboard',
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_verbs(request):
    error = None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            base = request.POST.get('base', '').strip().lower()
            past = request.POST.get('past', '').strip().lower()
            pp   = request.POST.get('pp',   '').strip().lower()
            if not base or not past or not pp:
                error = 'All three fields are required.'
            elif IrregularVerb.objects.filter(base=base).exists():
                error = f'Verb "{base}" already exists.'
            else:
                IrregularVerb.objects.create(base=base, past=past, pp=pp)
                messages.success(request, f'Verb "{base}" added successfully!')
                return redirect('admin_verbs')
        elif action == 'delete':
            IrregularVerb.objects.filter(id=request.POST.get('verb_id')).delete()
            messages.success(request, 'Verb deleted.')
            return redirect('admin_verbs')

    return render(request, 'admin_panel/verbs.html', {
        'verbs':      IrregularVerb.objects.all(),
        'error':      error,
        'active_tab': 'verbs',
    })


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_sessions(request):
    return render(request, 'admin_panel/sessions.html', {
        'sessions':   GameSession.objects.all(),
        'active_tab': 'sessions',
    })


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_delete_session(request, pk):
    if request.method == 'POST':
        GameSession.objects.filter(pk=pk).delete()
        messages.success(request, 'Session deleted.')
    return redirect('admin_sessions')


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_session_snapshots(request, pk):
    session   = get_object_or_404(GameSession, pk=pk)
    snapshots = session.snapshots.all()
    return render(request, 'admin_panel/snapshots.html', {
        'session':    session,
        'snapshots':  snapshots,
        'active_tab': 'sessions',
    })


# ─── ADMIN PANEL: STATISTICS (for advertisers / growth reporting) ─────────

@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_stats(request):
    today = timezone.localdate()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_players = Player.objects.count()
    dau = Player.objects.filter(last_active_date=today).count()
    wau = Player.objects.filter(last_active_date__gte=week_ago).count()
    mau = Player.objects.filter(last_active_date__gte=month_ago).count()

    new_players_7d = Player.objects.filter(created_at__date__gte=week_ago).count()
    new_players_30d = Player.objects.filter(created_at__date__gte=month_ago).count()

    total_sessions = GamePlaySession.objects.count()
    game_labels = dict(GamePlaySession.GAME_CHOICES)
    sessions_by_game_qs = list(
        GamePlaySession.objects.values('game_type').annotate(count=Count('id')).order_by('-count')
    )
    max_game_count = max([row['count'] for row in sessions_by_game_qs], default=0)
    sessions_by_game = [
        {
            'label': game_labels.get(row['game_type'], row['game_type']),
            'count': row['count'],
            'pct': round(row['count'] / max_game_count * 100) if max_game_count else 0,
        }
        for row in sessions_by_game_qs
    ]

    avg_duration = GamePlaySession.objects.aggregate(avg=Avg('duration_seconds'))['avg'] or 0
    total_xp_awarded = Player.objects.aggregate(s=Sum('xp'))['s'] or 0
    total_coins = Player.objects.aggregate(s=Sum('coins'))['s'] or 0

    streak_3plus = Player.objects.filter(current_streak__gte=3).count()
    streak_7plus = Player.objects.filter(current_streak__gte=7).count()

    context = {
        'total_players': total_players,
        'dau': dau, 'wau': wau, 'mau': mau,
        'new_players_7d': new_players_7d,
        'new_players_30d': new_players_30d,
        'total_sessions': total_sessions,
        'sessions_by_game': sessions_by_game,
        'avg_duration': round(avg_duration),
        'total_xp_awarded': total_xp_awarded,
        'total_coins': total_coins,
        'streak_3plus': streak_3plus,
        'streak_7plus': streak_7plus,
        'streak_3plus_pct': round(streak_3plus / total_players * 100) if total_players else 0,
        'streak_7plus_pct': round(streak_7plus / total_players * 100) if total_players else 0,
        'total_achievements_unlocked': PlayerAchievement.objects.count(),
        'top_players': Player.objects.order_by('-xp')[:10],
        'active_tab': 'stats',
    }
    return render(request, 'admin_panel/stats.html', context)