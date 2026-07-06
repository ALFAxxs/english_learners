from django.core.management.base import BaseCommand
from gamification.models import Achievement
from gamification.services import xp_for_next_level

# (code, title, description, icon, xp_reward, coin_reward, condition_type, condition_value)
ACHIEVEMENTS = [
    ("first_steps", "First Steps", "Play your first game", "🎮", 20, 10, "games_played", 1),
    ("dedicated_learner", "Dedicated Learner", "Play 10 games", "📚", 50, 25, "games_played", 10),
    ("game_master", "Game Master", "Play 50 games", "🎓", 150, 75, "games_played", 50),

    ("streak_7", "Week Warrior", "Reach a 7-day streak", "🔥", 100, 50, "streak", 7),
    ("streak_30", "Unstoppable", "Reach a 30-day streak", "💎", 400, 200, "streak", 30),

    ("level_5", "Rising Star", "Reach Level 5", "⭐", 0, 50, "total_xp", xp_for_next_level(4)),
    ("level_10", "Champion", "Reach Level 10", "🌠", 0, 100, "total_xp", xp_for_next_level(9)),
    ("level_20", "Legend", "Reach Level 20", "👑", 0, 250, "total_xp", xp_for_next_level(19)),

    ("perfectionist", "Perfectionist", "Get a perfect score in any game", "💯", 60, 30, "game_perfect_score", 1),
    ("combo_king", "Combo King", "Reach a 10x combo", "⚡", 80, 40, "combo", 10),
    ("combo_legend", "Combo Legend", "Reach a 20x combo", "🌟", 150, 70, "combo", 20),

    ("coin_collector", "Coin Collector", "Earn 500 coins total", "🪙", 60, 0, "coins_earned", 500),

    ("word_wizard", "Word Wizard", "Find 50 words in Word Hunter", "🔍", 100, 50, "word_hunter_words_found", 50),
    ("word_legend", "Word Legend", "Find 200 words in Word Hunter", "🏹", 250, 120, "word_hunter_words_found", 200),

    ("memory_master", "Memory Master", "Complete 20 Memory Cards sessions", "🃏", 100, 50, "memory_cards_completed", 20),
]


class Command(BaseCommand):
    help = "Seed the achievement definitions."

    def handle(self, *args, **options):
        created = 0
        for code, title, desc, icon, xp, coins, cond_type, cond_value in ACHIEVEMENTS:
            _, was_created = Achievement.objects.get_or_create(
                code=code,
                defaults={
                    'title': title, 'description': desc, 'icon': icon,
                    'xp_reward': xp, 'coin_reward': coins,
                    'condition_type': cond_type, 'condition_value': cond_value,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} new achievements ({Achievement.objects.count()} total)."
        ))
