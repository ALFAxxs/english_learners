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

    ("grammar_novice", "Grammar Novice", "Complete your first Grammar Battle topic", "📘", 60, 30, "grammar_topics_completed", 1),
    ("grammar_master", "Grammar Master", "Complete all 12 Grammar Battle topics", "🎓", 300, 150, "grammar_topics_completed", 12),
    ("boss_slayer", "Boss Slayer", "Clear 10 Grammar Battle boss rounds", "⚔️", 150, 75, "boss_rounds_cleared", 10),

    ("survival_first", "First Contact", "Reach a good ending in your first Daily Survival scenario", "🧳", 60, 30, "survival_scenarios_completed", 1),
    ("world_traveler", "World Traveler", "Reach a good ending in all 16 Daily Survival scenarios", "🌍", 300, 150, "survival_scenarios_completed", 16),

    ("bookworm", "Bookworm", "Complete your first Vocabulary Builder unit", "📖", 60, 30, "vocab_units_completed", 1),
    ("vocabulary_master", "Vocabulary Master", "Complete all 30 Vocabulary Builder units", "🎓", 400, 200, "vocab_units_completed", 30),
]


class Command(BaseCommand):
    help = "Seed the achievement definitions."

    def handle(self, *args, **options):
        created = 0
        for code, title, desc, icon, xp, coins, cond_type, cond_value in ACHIEVEMENTS:
            achievement, was_created = Achievement.objects.get_or_create(
                code=code,
                defaults={
                    'title': title, 'description': desc, 'icon': icon,
                    'xp_reward': xp, 'coin_reward': coins,
                    'condition_type': cond_type, 'condition_value': cond_value,
                },
            )
            if was_created:
                created += 1
            else:
                # Backfill/refresh in case content (e.g. topic/scenario counts) changed since
                # this achievement was first seeded.
                achievement.title = title
                achievement.description = desc
                achievement.icon = icon
                achievement.xp_reward = xp
                achievement.coin_reward = coins
                achievement.condition_type = cond_type
                achievement.condition_value = cond_value
                achievement.save()
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} new achievements ({Achievement.objects.count()} total)."
        ))
