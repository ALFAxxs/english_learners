from django.core.management.base import BaseCommand
from gamification.models import VocabWord

# (word, meaning, category, difficulty)
WORDS = [
    # ── TRAVEL ──────────────────────────────────────────────────────────
    ("hotel", "a place where travelers pay to sleep and stay", "travel", 1),
    ("taxi", "a car that drives you somewhere for money", "travel", 1),
    ("map", "a drawing that shows where places are", "travel", 1),
    ("ticket", "a paper that lets you travel or enter somewhere", "travel", 1),
    ("luggage", "the bags you take when you travel", "travel", 1),
    ("subway", "an underground train system in a city", "travel", 1),
    ("airport", "a place where planes take off and land", "travel", 1),
    ("journey", "a trip from one place to another", "travel", 2),
    ("airline", "a company that operates airplanes", "travel", 2),
    ("customs", "the place at a border where bags are checked", "travel", 2),
    ("boarding", "getting onto a plane, train or ship", "travel", 2),
    ("suitcase", "a case used for carrying clothes while traveling", "travel", 2),
    ("passport", "an official document needed to travel abroad", "travel", 2),
    ("layover", "a stop between two flights", "travel", 2),
    ("itinerary", "a planned route or schedule of a trip", "travel", 3),
    ("destination", "the place someone is traveling to", "travel", 3),
    ("immigration", "the control of people entering a country", "travel", 3),
    ("reservation", "an arrangement to have something held for you", "travel", 3),

    # ── FOOD ────────────────────────────────────────────────────────────
    ("bread", "a food made from baked flour and water", "food", 1),
    ("apple", "a round, crisp fruit that grows on trees", "food", 1),
    ("juice", "a drink made from fruit", "food", 1),
    ("salad", "a mix of vegetables eaten cold", "food", 1),
    ("cheese", "a food made from milk", "food", 1),
    ("dinner", "the main meal eaten in the evening", "food", 1),
    ("recipe", "instructions for cooking a dish", "food", 1),
    ("sandwich", "food made of bread with filling inside", "food", 2),
    ("beverage", "a drink of any kind", "food", 2),
    ("grocery", "food and household items you buy at a store", "food", 2),
    ("dessert", "a sweet dish eaten after a meal", "food", 2),
    ("breakfast", "the first meal of the day", "food", 2),
    ("appetizer", "a small dish served before the main meal", "food", 2),
    ("leftover", "food that remains after a meal", "food", 2),
    ("restaurant", "a place where you pay to eat a meal", "food", 3),
    ("vegetarian", "a person who does not eat meat", "food", 3),
    ("ingredient", "one item used to make a dish", "food", 3),
    ("nutritious", "good for your health when eaten", "food", 3),

    # ── WORK ────────────────────────────────────────────────────────────
    ("office", "a room or building where people work", "work", 1),
    ("salary", "money paid regularly for doing a job", "work", 1),
    ("resume", "a document listing your job history", "work", 1),
    ("career", "the jobs a person has over their life", "work", 1),
    ("manager", "a person who leads a team at work", "work", 1),
    ("meeting", "when people gather to discuss something", "work", 1),
    ("deadline", "the time by which something must be finished", "work", 2),
    ("employee", "a person who works for a company", "work", 2),
    ("contract", "a written agreement between two parties", "work", 2),
    ("colleague", "a person you work with", "work", 2),
    ("interview", "a meeting to ask someone questions for a job", "work", 2),
    ("promotion", "moving up to a higher position at work", "work", 2),
    ("overtime", "extra time worked beyond normal hours", "work", 2),
    ("negotiation", "a discussion to reach an agreement", "work", 3),
    ("application", "a formal request, often for a job", "work", 3),
    ("supervisor", "a person who oversees other workers", "work", 3),
    ("qualification", "a skill needed for a job or task", "work", 3),

    # ── DAILY LIFE ──────────────────────────────────────────────────────
    ("clock", "a device that shows the time", "daily", 1),
    ("mirror", "a surface that reflects your image", "daily", 1),
    ("kitchen", "a room where food is cooked", "daily", 1),
    ("shower", "a wash using falling water", "daily", 1),
    ("laundry", "clothes that need washing", "daily", 1),
    ("calendar", "a chart that shows days and months", "daily", 2),
    ("neighbor", "a person who lives near you", "daily", 2),
    ("errand", "a short trip to do a task", "daily", 2),
    ("schedule", "a plan of times for events", "daily", 2),
    ("chores", "small regular household tasks", "daily", 2),
    ("routine", "a regular way of doing things", "daily", 2),
    ("apartment", "a set of rooms for living in a building", "daily", 2),
    ("appliance", "a machine used at home, like a fridge", "daily", 3),
    ("furniture", "large movable items like tables and chairs", "daily", 3),
    ("household", "relating to a home and the people in it", "daily", 3),

    # ── HEALTH ──────────────────────────────────────────────────────────
    ("doctor", "a person trained to treat illness", "health", 1),
    ("nurse", "a person trained to care for the sick", "health", 1),
    ("fever", "a higher than normal body temperature", "health", 1),
    ("clinic", "a place where people get medical care", "health", 1),
    ("tablet", "a small pill of medicine", "health", 1),
    ("healthy", "in good physical condition", "health", 1),
    ("checkup", "a routine medical examination", "health", 2),
    ("symptom", "a sign that shows you are ill", "health", 2),
    ("medicine", "a substance used to treat illness", "health", 2),
    ("exercise", "physical activity to stay fit", "health", 2),
    ("recovery", "getting better after being sick", "health", 2),
    ("appointment", "a set time to see a doctor", "health", 3),
    ("diagnosis", "identifying what illness someone has", "health", 3),
    ("treatment", "medical care given for an illness", "health", 3),
    ("prescription", "a doctor's written order for medicine", "health", 3),

    # ── NATURE & WEATHER ───────────────────────────────────────────────
    ("cloud", "a mass of water vapor in the sky", "nature", 1),
    ("river", "a natural flowing stream of water", "nature", 1),
    ("forest", "a large area covered with trees", "nature", 1),
    ("desert", "a dry area with little rain", "nature", 1),
    ("breeze", "a gentle wind", "nature", 1),
    ("thunder", "the loud sound after lightning", "nature", 1),
    ("drought", "a long period without rain", "nature", 2),
    ("rainbow", "an arc of colors seen after rain", "nature", 2),
    ("mountain", "a very high, natural raised landform", "nature", 2),
    ("humidity", "the amount of moisture in the air", "nature", 2),
    ("blizzard", "a severe snowstorm with strong wind", "nature", 2),
    ("temperature", "how hot or cold something is", "nature", 3),
    ("atmosphere", "the layer of gases around the earth", "nature", 3),
    ("environment", "the natural world around us", "nature", 3),
]


class Command(BaseCommand):
    help = "Seed the vocabulary word bank used by Word Hunter and Memory Cards."

    def handle(self, *args, **options):
        created = 0
        for word, meaning, category, difficulty in WORDS:
            _, was_created = VocabWord.objects.get_or_create(
                word=word,
                defaults={'meaning': meaning, 'category': category, 'difficulty': difficulty},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} new words ({VocabWord.objects.count()} total in bank)."
        ))
