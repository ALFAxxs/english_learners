import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from django.contrib import messages

from .models import IrregularVerb, GameSession


def is_staff(user):
    return user.is_authenticated and user.is_staff


# ─── MAIN APP (SPA page) ───────────────────────────────────────────────────

def index(request):
    """Single page — the whole SPA loads here."""
    return render(request, 'game/index.html')


# ─── API: VERBS ────────────────────────────────────────────────────────────

def api_verbs(request):
    """Return all verbs as JSON for the frontend."""
    verbs = list(IrregularVerb.objects.values('id', 'base', 'past', 'pp'))
    return JsonResponse({'verbs': verbs})


# ─── API: SAVE SESSION ─────────────────────────────────────────────────────

@require_POST
def api_save_session(request):
    """Save a completed game session."""
    try:
        data = json.loads(request.body)
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


# ─── ADMIN PANEL ───────────────────────────────────────────────────────────

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_panel/login.html', {'error': True})

    return render(request, 'admin_panel/login.html', {'error': False})


def admin_logout_view(request):
    logout(request)
    return redirect('index')


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_dashboard(request):
    total_verbs = IrregularVerb.objects.count()
    total_sessions = GameSession.objects.count()
    avg_score = GameSession.objects.aggregate(avg=Avg('score_pct'))['avg'] or 0
    unique_players = GameSession.objects.values('player_name').distinct().count()
    recent_sessions = GameSession.objects.all()[:10]

    context = {
        'total_verbs': total_verbs,
        'total_sessions': total_sessions,
        'avg_score': round(avg_score),
        'unique_players': unique_players,
        'recent_sessions': recent_sessions,
        'active_tab': 'dashboard',
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
            pp = request.POST.get('pp', '').strip().lower()
            if not base or not past or not pp:
                error = 'All three fields are required.'
            elif IrregularVerb.objects.filter(base=base).exists():
                error = f'Verb "{base}" already exists.'
            else:
                IrregularVerb.objects.create(base=base, past=past, pp=pp)
                messages.success(request, f'Verb "{base}" added successfully!')
                return redirect('admin_verbs')

        elif action == 'delete':
            verb_id = request.POST.get('verb_id')
            IrregularVerb.objects.filter(id=verb_id).delete()
            messages.success(request, 'Verb deleted.')
            return redirect('admin_verbs')

    verbs = IrregularVerb.objects.all()
    context = {
        'verbs': verbs,
        'error': error,
        'active_tab': 'verbs',
    }
    return render(request, 'admin_panel/verbs.html', context)


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_sessions(request):
    sessions = GameSession.objects.all()
    context = {
        'sessions': sessions,
        'active_tab': 'sessions',
    }
    return render(request, 'admin_panel/sessions.html', context)


@login_required
@user_passes_test(is_staff, login_url='/admin-panel/login/')
def admin_delete_session(request, pk):
    if request.method == 'POST':
        GameSession.objects.filter(pk=pk).delete()
        messages.success(request, 'Session deleted.')
    return redirect('admin_sessions')


def error_400(request, exception=None):
    return render(request, '400.html', status=400)

def error_403(request, exception=None):
    return render(request, '403.html', status=403)


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def error_500(request, exception=None):
    return render(request, '500.html', status=500)
