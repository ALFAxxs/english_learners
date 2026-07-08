from django.core.management.base import BaseCommand
from gamification.models import GrammarTopic, GrammarQuestion

# Each topic: name, icon, description, lesson_rule, lesson_examples, questions
# Each question: (question_type, prompt, options, correct_answer, is_boss)
TOPICS = [
    {
        'name': "Present Simple & Continuous", 'icon': "☀️",
        'description': "Everyday actions vs. actions happening right now.",
        'lesson_rule': "The Present Simple describes habits, routines, permanent facts, and things "
                        "that are generally true. The Present Continuous (am/is/are + verb-ing) "
                        "describes actions happening at this exact moment, temporary situations, "
                        "or fixed future arrangements. Some verbs (like, know, want, believe) "
                        "describe states, not actions, so they are usually not used in the "
                        "continuous form.",
        'lesson_structure': "Present Simple — positive: I/You/We/They + verb; He/She/It + verb+s/es. "
                             "Negative: don't/doesn't + verb. Question: Do/Does + subject + verb? "
                             "Present Continuous — positive: am/is/are + verb-ing. Negative: am/is/are "
                             "+ not + verb-ing. Question: Am/Is/Are + subject + verb-ing?",
        'lesson_signal_words': ["always", "usually", "often", "sometimes", "never", "every day/week",
                                 "on Mondays", "now", "right now", "at the moment", "Look!", "Listen!"],
        'lesson_examples': [
            "She works in a bank. (habit)",
            "She doesn't work on weekends. (negative)",
            "Does she work here? (question)",
            "Water boils at 100°C. (general fact)",
            "I am working on a report right now. (happening now)",
            "They are not studying at the moment.",
            "Are you listening to me?",
            "We are meeting him tomorrow at 5. (fixed arrangement)",
        ],
        'lesson_common_mistakes': [
            "❌ She go to school. → ✅ She goes to school. (add -s/-es for he/she/it)",
            "❌ I am liking this song. → ✅ I like this song. (state verbs aren't used in the continuous form)",
            "❌ Does she goes there? → ✅ Does she go there? (only one verb form changes after does)",
            "❌ I am not knowing the answer. → ✅ I don't know the answer.",
        ],
        'questions': [
            ('multiple_choice', "She ___ to work every day.", ["goes", "go", "going", "gone"], "goes", False),
            ('multiple_choice', "Look! It ___ outside.", ["rains", "rain", "is raining", "raining"], "is raining", False),
            ('fill_blank', "He usually ___ (drink) coffee in the morning.", [], "drinks", False),
            ('fill_blank', "They ___ (not/like) horror movies.", [], "don't like", False),
            ('multiple_choice', "I ___ my homework right now.", ["do", "am doing", "does", "did"], "am doing", False),
            ('multiple_choice', "Water ___ at 100 degrees Celsius.", ["boil", "boils", "is boiling", "boiled"], "boils", False),
            ('fill_blank', "We ___ (study) English at the moment.", [], "are studying", False),
            ('multiple_choice', "My brother ___ football on Saturdays.", ["play", "plays", "is playing", "played"], "plays", False),
            ('drag_drop', "Put the words in order.", ["does", "she", "work", "where", "?"], "Where does she work?", False),
            ('drag_drop', "Put the words in order.", ["always", "late", "he", "is"], "He is always late", False),
            ('fill_blank', "Listen! Someone ___ (knock) at the door.", [], "is knocking", False),
            ('multiple_choice', "I ___ understand this question.", ["don't", "doesn't", "am not", "isn't"], "don't", False),
            ('multiple_choice', "The train ___ at 9 AM every day.", ["leave", "leaves", "is leaving", "left"], "leaves", False),
            ('fill_blank', "I ___ (not/watch) TV right now; I'm reading.", [], "am not watching", False),
            ('multiple_choice', "___ your sister live near here?", ["Do", "Does", "Is", "Are"], "Does", False),
            ('drag_drop', "Put the words in order.", ["cook", "never", "dinner", "I"], "I never cook dinner", False),
            ('fill_blank', "Why ___ (you/laugh)?", [], "are you laughing", False),
            ('multiple_choice', "Which sentence is correct?", ["She don't like tea.", "She doesn't likes tea.", "She doesn't like tea.", "She not like tea."], "She doesn't like tea.", True),
            ('fill_blank', "He ___ (not/work) today because he is sick.", [], "isn't working", True),
            ('multiple_choice', "Choose the correct question:", ["Does she works on Sundays?", "Does she work on Sundays?", "Is she works on Sundays?", "Do she work on Sundays?"], "Does she work on Sundays?", True),
        ],
    },
    {
        'name': "Past Tenses", 'icon': "⏳",
        'description': "Simple past, past continuous and present perfect.",
        'lesson_rule': "The Past Simple describes a finished action at a specific past time. The "
                        "Past Continuous describes an action in progress at a certain past moment, "
                        "often interrupted by another action. The Present Perfect connects a past "
                        "action to the present — either the exact time isn't stated, or the result "
                        "still matters now.",
        'lesson_structure': "Past Simple: verb+ed (regular) or irregular form. Negative: didn't + "
                             "base verb. Question: Did + subject + base verb? Past Continuous: "
                             "was/were + verb-ing. Present Perfect: have/has + past participle.",
        'lesson_signal_words': ["yesterday", "last week/year", "in 2010", "ago", "when", "while",
                                 "already", "just", "yet", "ever", "never", "since", "for"],
        'lesson_examples': [
            "I visited my grandmother last week.",
            "I didn't go to the party yesterday.",
            "Did you see that movie?",
            "While I was cooking, the phone rang.",
            "She was sleeping when I called.",
            "She has already finished her homework.",
            "Have you ever been to London?",
            "They haven't arrived yet.",
        ],
        'lesson_common_mistakes': [
            "❌ I have seen him yesterday. → ✅ I saw him yesterday. (don't use Present Perfect with a specific past time word)",
            "❌ She go there last year. → ✅ She went there last year.",
            "❌ I didn't went. → ✅ I didn't go. (base form after didn't)",
            "❌ Since three years. → ✅ For three years. (since + point in time, for + duration)",
        ],
        'questions': [
            ('multiple_choice', "She ___ to Paris last year.", ["go", "goes", "went", "gone"], "went", False),
            ('fill_blank', "I ___ (see) that movie yesterday.", [], "saw", False),
            ('multiple_choice', "While I ___ dinner, the phone rang.", ["cooked", "was cooking", "cook", "cooking"], "was cooking", False),
            ('fill_blank', "They ___ (not/finish) the project yet.", [], "haven't finished", False),
            ('multiple_choice', "Have you ever ___ to Japan?", ["go", "went", "gone", "been"], "been", False),
            ('drag_drop', "Put the words in order.", ["did", "you", "what", "yesterday", "do", "?"], "What did you do yesterday?", False),
            ('fill_blank', "He ___ (live) in London five years ago.", [], "lived", False),
            ('multiple_choice', "Yesterday, it ___ a lot.", ["rain", "rains", "rained", "raining"], "rained", False),
            ('fill_blank', "She ___ (not/go) to school last Monday.", [], "didn't go", False),
            ('drag_drop', "Put the words in order.", ["night", "last", "homework", "I", "did", "my"], "I did my homework last night", False),
            ('multiple_choice', "I have ___ finished my homework.", ["already", "yesterday", "ago", "last"], "already", False),
            ('fill_blank', "___ (you/eat) breakfast this morning?", [], "Did you eat", False),
            ('multiple_choice', "We ___ finished eating when she called.", ["have", "had", "has", "having"], "had", False),
            ('fill_blank', "I ___ (just/arrive) home.", [], "have just arrived", False),
            ('multiple_choice', "She was reading a book ___ I came in.", ["when", "while", "since", "for"], "when", False),
            ('drag_drop', "Put the words in order.", ["born", "was", "I", "Tashkent", "in"], "I was born in Tashkent", False),
            ('fill_blank', "___ (they/live) here for ten years now.", [], "Have they lived", False),
            ('fill_blank', "When I arrived, they ___ (already/leave).", [], "had already left", True),
            ('multiple_choice', "Choose the correct sentence:", ["I have seen him yesterday.", "I saw him yesterday.", "I have saw him yesterday.", "I seen him yesterday."], "I saw him yesterday.", True),
            ('fill_blank', "By the time the movie started, we ___ (already/find) our seats.", [], "had already found", True),
        ],
    },
    {
        'name': "Future Forms (will / going to)", 'icon': "🔮",
        'description': "Predictions, plans and spontaneous decisions.",
        'lesson_rule': "Use 'will' for spontaneous decisions made at the moment of speaking, "
                        "predictions without strong evidence, promises, and offers. Use 'be going "
                        "to' for plans already decided before speaking, and predictions based on "
                        "something you can see or know right now. The Present Continuous can also "
                        "express fixed future arrangements.",
        'lesson_structure': "will: subject + will + base verb. Negative: won't + base verb. "
                             "be going to: subject + am/is/are + going to + base verb.",
        'lesson_signal_words': ["tomorrow", "next week/year", "soon", "I think...", "probably",
                                 "I promise", "Look at...!"],
        'lesson_examples': [
            "I think it will rain tomorrow. (prediction, no strong evidence)",
            "I'll answer the phone. (spontaneous decision)",
            "I promise I will call you. (promise)",
            "I'm going to study medicine after school. (already-made plan)",
            "Look at those clouds — it's going to rain! (evidence now)",
            "We are going to visit Samarkand next month.",
            "She isn't going to come to the party.",
            "We are meeting the client at 3 PM tomorrow. (fixed arrangement)",
        ],
        'lesson_common_mistakes': [
            "❌ I will going to study. → ✅ I am going to study. (don't mix will + going to)",
            "❌ I am go to travel. → ✅ I am going to travel.",
            "❌ It will going to rain. → ✅ It is going to rain.",
            "❌ I will visit her tomorrow (if it's already decided) → ✅ I'm going to visit her tomorrow.",
        ],
        'questions': [
            ('multiple_choice', "Look at the sky! It ___ rain.", ["will", "is going to", "would", "was going to"], "is going to", False),
            ('fill_blank', "I think she ___ (win) the competition.", [], "will win", False),
            ('multiple_choice', "I've decided — I ___ join the gym next week.", ["will", "am going to", "would", "was"], "am going to", False),
            ('fill_blank', "The phone is ringing. I ___ (answer) it.", [], "will answer", False),
            ('multiple_choice', "___ you help me carry this box?", ["Will", "Are going", "Would", "Did"], "Will", False),
            ('drag_drop', "Put the words in order.", ["trip", "going", "we", "a", "take", "to", "are"], "We are going to take a trip", False),
            ('multiple_choice', "I promise I ___ call you when I arrive.", ["will", "am going to", "would", "was going to"], "will", False),
            ('fill_blank', "They ___ (move) to a new house next month. (already planned)", [], "are going to move", False),
            ('multiple_choice', "According to the forecast, it ___ be sunny tomorrow.", ["will", "is going to", "would", "was"], "is going to", False),
            ('drag_drop', "Put the words in order.", ["you", "what", "do", "tonight", "going", "are", "to"], "What are you going to do tonight?", False),
            ('fill_blank', "Don't worry, I ___ (help) you with your homework.", [], "will help", False),
            ('multiple_choice', "She has already packed her bags — she ___ travel soon.", ["will", "is going to", "would", "was going to"], "is going to", False),
            ('fill_blank', "___ (you/be) at the meeting tomorrow?", [], "Will you be", False),
            ('multiple_choice', "I ___ probably stay home this weekend.", ["will", "am going to", "would", "was"], "will", False),
            ('drag_drop', "Put the words in order.", ["rain", "think", "it", "will", "I"], "I think it will rain", False),
            ('fill_blank', "We ___ (not/go) out tonight; we're too tired.", [], "are not going to", False),
            ('multiple_choice', "Which sentence is a spontaneous offer?", ["I'm going to visit my grandmother.", "I'll carry that bag for you.", "I am meeting him at 5.", "I was going to call."], "I'll carry that bag for you.", False),
            ('multiple_choice', "Which sentence expresses a planned decision, not a spontaneous one?", ["I'll get you a coffee.", "I'm going to visit my grandmother this weekend.", "I'll help you now.", "I'll answer that."], "I'm going to visit my grandmother this weekend.", True),
            ('fill_blank', "By next year, they ___ (complete) the new building.", [], "will have completed", True),
            ('multiple_choice', "Choose the correct sentence:", ["I will going to study.", "I am will study.", "I am going to study.", "I going to study."], "I am going to study.", True),
        ],
    },
    {
        'name': "Present Perfect vs Past Simple", 'icon': "🕰️",
        'description': "Connecting the past to now vs. a finished, specific time.",
        'lesson_rule': "Use the Present Perfect for actions at an unspecified past time, or when "
                        "the result is still important now. Use the Past Simple when you say or "
                        "know exactly when something happened. Simple rule: if there's a specific "
                        "time word (yesterday, in 2020, last week), use the Past Simple, not the "
                        "Present Perfect.",
        'lesson_structure': "Present Perfect: have/has + past participle. Past Simple: verb+ed "
                             "(regular) or irregular form.",
        'lesson_signal_words': ["already", "just", "yet", "ever", "never", "since", "for",
                                 "so far (Present Perfect)", "yesterday", "last year", "ago",
                                 "in 2005", "when (Past Simple)"],
        'lesson_examples': [
            "I have visited London twice. (unspecified time)",
            "I visited London in 2019. (specific time)",
            "She has just finished her homework.",
            "She finished her homework an hour ago.",
            "Have you ever eaten sushi?",
            "I ate sushi last night.",
            "They haven't seen that film yet.",
            "They saw that film last weekend.",
        ],
        'lesson_common_mistakes': [
            "❌ I have seen him yesterday. → ✅ I saw him yesterday.",
            "❌ I have been born in 1998. → ✅ I was born in 1998. (a specific past event uses the Past Simple)",
            "❌ She lived here since 2015. → ✅ She has lived here since 2015. (ongoing situation → Present Perfect)",
            "❌ Did you ever visit Paris? → ✅ Have you ever visited Paris? (more natural with Present Perfect)",
        ],
        'questions': [
            ('multiple_choice', "I ___ this movie before.", ["saw", "have seen", "see", "seeing"], "have seen", False),
            ('fill_blank', "She ___ (visit) Paris last summer.", [], "visited", False),
            ('multiple_choice', "___ you finished your homework yet?", ["Did", "Have", "Do", "Were"], "Have", False),
            ('fill_blank', "He ___ (lose) his keys yesterday.", [], "lost", False),
            ('multiple_choice', "I have known her ___ 2015.", ["for", "since", "ago", "in"], "since", False),
            ('drag_drop', "Put the words in order.", ["years", "lived", "three", "here", "I", "for", "have"], "I have lived here for three years", False),
            ('fill_blank', "They ___ (not/see) that film yet.", [], "haven't seen", False),
            ('multiple_choice', "We went to Italy ___.", ["since 2018", "for 2018", "last year", "yet"], "last year", False),
            ('fill_blank', "___ (you/ever/be) to Egypt?", [], "Have you ever been", False),
            ('multiple_choice', "She ___ her car two days ago.", ["has sold", "sold", "sells", "selling"], "sold", False),
            ('drag_drop', "Put the words in order.", ["yet", "finished", "haven't", "I", "my", "homework"], "I haven't finished my homework yet", False),
            ('fill_blank', "I ___ (already/eat) breakfast, so I'm not hungry.", [], "have already eaten", False),
            ('multiple_choice', "He arrived in Tashkent ___.", ["since Monday", "for two days", "yesterday", "yet"], "yesterday", False),
            ('fill_blank', "___ (she/complete) the report?", [], "Has she completed", False),
            ('multiple_choice', "I have never ___ such a beautiful place.", ["see", "saw", "seen", "seeing"], "seen", False),
            ('drag_drop', "Put the words in order.", ["ago", "met", "two", "we", "years"], "We met two years ago", False),
            ('fill_blank', "My grandfather ___ (die) in 2005.", [], "died", False),
            ('multiple_choice', "Choose the correct sentence:", ["I have seen him yesterday.", "I saw him yesterday.", "I have saw him yesterday.", "I did seen him yesterday."], "I saw him yesterday.", True),
            ('fill_blank', "She ___ (work) here since 2010 and is still working here now.", [], "has worked", True),
            ('multiple_choice', "Which time expression is used with the Present Perfect?", ["yesterday", "last week", "ago", "already"], "already", True),
        ],
    },
    {
        'name': "Articles (a / an / the)", 'icon': "📰",
        'description': "Choosing a, an, the, or no article at all.",
        'lesson_rule': "Use 'a/an' the first time you mention a singular countable noun ('an' "
                        "before vowel sounds, not just vowel letters). Use 'the' when the listener "
                        "already knows which one you mean — because it was mentioned before, "
                        "there's only one, or it's specific. Use no article with plural or "
                        "uncountable nouns when speaking generally.",
        'lesson_structure': "a/an + singular countable noun (first mention). the + any noun "
                             "(specific/already known). (no article) + plural/uncountable noun "
                             "(general statement).",
        'lesson_signal_words': ["a/an (first mention)", "the (specific, already known, unique "
                                 "things: the sun, the moon)", "no article (general plurals/"
                                 "uncountables: Dogs are loyal, Milk is healthy)"],
        'lesson_examples': [
            "I saw a dog in the park. (first mention)",
            "The dog was very friendly. (same dog, now known)",
            "She is an engineer. (an before a vowel sound)",
            "The sun rises in the east. (only one sun)",
            "Dogs are loyal animals. (general statement, no article)",
            "I love the sound of rain. (specific sound)",
            "He plays the guitar every evening. (specific, known activity)",
            "I go to school by bus. (school as an institution, no article)",
        ],
        'lesson_common_mistakes': [
            "❌ I have an car. → ✅ I have a car. (an only before vowel SOUNDS: an hour, a university)",
            "❌ I saw a elephant. → ✅ I saw an elephant.",
            "❌ The dogs are loyal animals. → ✅ Dogs are loyal animals. (remove 'the' when speaking generally)",
            "❌ I go to the school by the bus. → ✅ I go to school by bus. (no article for institutions used generally)",
        ],
        'questions': [
            ('multiple_choice', "I saw ___ elephant at the zoo.", ["a", "an", "the", "-"], "an", False),
            ('multiple_choice', "___ sun rises in the east.", ["A", "An", "The", "-"], "The", False),
            ('fill_blank', "She is ___ engineer.", [], "an", False),
            ('fill_blank', "I need ___ umbrella; it's raining.", [], "an", False),
            ('multiple_choice', "He plays ___ guitar every evening.", ["a", "an", "the", "-"], "the", False),
            ('multiple_choice', "___ dogs are loyal animals. (general statement)", ["A", "An", "The", "-"], "-", False),
            ('fill_blank', "This is ___ best day of my life!", [], "the", False),
            ('multiple_choice', "We stayed at ___ hotel near the beach.", ["a", "an", "the", "-"], "a", False),
            ('fill_blank', "___ apple a day keeps the doctor away.", [], "An", False),
            ('drag_drop', "Put the words in order.", ["book", "the", "table", "is", "on"], "The book is on the table", False),
            ('multiple_choice', "I want to be ___ doctor when I grow up.", ["a", "an", "the", "-"], "a", False),
            ('fill_blank', "Can you pass me ___ salt, please?", [], "the", False),
            ('multiple_choice', "___ Moon orbits the Earth.", ["A", "An", "The", "-"], "The", False),
            ('multiple_choice', "I go to ___ school by bus.", ["a", "an", "the", "-"], "-", False),
            ('fill_blank', "He is ___ honest man.", [], "an", False),
            ('drag_drop', "Put the words in order.", ["read", "book", "interesting", "an", "I"], "I read an interesting book", False),
            ('fill_blank', "She wants to become ___ actress.", [], "an", False),
            ('multiple_choice', "Which is correct?", ["I have an car.", "I have a car.", "I have the car.", "I have car."], "I have a car.", True),
            ('multiple_choice', "___ Nile is the longest river in Africa.", ["A", "An", "The", "-"], "The", True),
            ('multiple_choice', "Which sentence uses articles correctly?", ["I saw a elephant.", "I saw an elephant.", "I saw the a elephant.", "I saw elephant."], "I saw an elephant.", True),
        ],
    },
    {
        'name': "Prepositions", 'icon': "🧭",
        'description': "Prepositions of time, place and movement.",
        'lesson_rule': "Prepositions of time (at, on, in), place (in, on, under, between) and "
                        "other relationships (for, of, to, with) show how things connect. Time: "
                        "'at' for exact times/points (at 5 PM, at night), 'on' for days/dates (on "
                        "Monday), 'in' for longer periods (in July, in 2020). Place: 'in' for "
                        "enclosed spaces, 'on' for surfaces, 'at' for specific points.",
        'lesson_structure': "Time: at + clock time/night · on + day/date · in + month/year/longer "
                             "period. Place: in + enclosed space · on + surface · at + specific point.",
        'lesson_signal_words': ["at 5 o'clock, at night, at the airport", "on Monday, on the table",
                                 "in July, in the box, in a village"],
        'lesson_examples': [
            "We meet at 6 PM. (exact time)",
            "The meeting is on Monday. (day)",
            "She was born in 1995. (year)",
            "The cat is under the table. (place)",
            "The book is on the table. (surface)",
            "We live in a small village. (enclosed area)",
            "She is good at math. (fixed expression)",
            "He is afraid of spiders. (fixed expression)",
        ],
        'lesson_common_mistakes': [
            "❌ I was born on 1995. → ✅ I was born in 1995. (years take 'in')",
            "❌ See you in Monday. → ✅ See you on Monday. (days take 'on')",
            "❌ She's good in math. → ✅ She's good at math. (fixed expression: good at)",
            "❌ Afraid from spiders. → ✅ Afraid of spiders.",
        ],
        'questions': [
            ('multiple_choice', "The book is ___ the table.", ["in", "on", "at", "under"], "on", False),
            ('fill_blank', "We arrived ___ the airport at noon.", [], "at", False),
            ('multiple_choice', "She was born ___ 1995.", ["in", "on", "at", "by"], "in", False),
            ('fill_blank', "The meeting is ___ Monday morning.", [], "on", False),
            ('multiple_choice', "I'll see you ___ 5 o'clock.", ["in", "on", "at", "since"], "at", False),
            ('fill_blank', "He is afraid ___ spiders.", [], "of", False),
            ('multiple_choice', "The cat is hiding ___ the sofa.", ["under", "on", "at", "to"], "under", False),
            ('drag_drop', "Put the words in order.", ["school", "to", "walk", "I", "every day"], "I walk to school every day", False),
            ('fill_blank', "She has been waiting ___ two hours.", [], "for", False),
            ('multiple_choice', "We live ___ a small village.", ["in", "on", "at", "to"], "in", False),
            ('fill_blank', "Turn left ___ the corner.", [], "at", False),
            ('multiple_choice', "This gift is ___ you.", ["for", "to", "of", "with"], "for", False),
            ('multiple_choice', "The plane arrives ___ 6 PM.", ["in", "on", "at", "by"], "at", False),
            ('fill_blank', "She is married ___ a doctor.", [], "to", False),
            ('multiple_choice', "The keys are ___ my bag.", ["in", "on", "at", "under"], "in", False),
            ('drag_drop', "Put the words in order.", ["the", "sat", "we", "beach", "on"], "We sat on the beach", False),
            ('fill_blank', "He apologized ___ being late.", [], "for", False),
            ('multiple_choice', "Choose the correct preposition: \"I'm looking ___ my keys.\"", ["for", "at", "on", "of"], "for", True),
            ('fill_blank', "She's good ___ playing the piano.", [], "at", True),
            ('fill_blank', "The store is ___ the bank and the post office.", [], "between", True),
        ],
    },
    {
        'name': "Comparatives & Superlatives", 'icon': "📏",
        'description': "Comparing two or more things.",
        'lesson_rule': "Use comparatives to compare exactly two things, and superlatives to "
                        "compare three or more (or to single out 'the most/least' of a group). "
                        "One-syllable adjectives usually add -er/-est (fast → faster → fastest). "
                        "Adjectives with two or more syllables usually use more/most (expensive → "
                        "more expensive → most expensive). Some adjectives are irregular (good → "
                        "better → best; bad → worse → worst).",
        'lesson_structure': "Comparative: adjective+er + than (short) / more + adjective + than "
                             "(long). Superlative: the + adjective+est (short) / the most + "
                             "adjective (long).",
        'lesson_signal_words': ["than (comparative)", "the ___est / the most ___ (superlative)",
                                 "as ___ as (equal comparison)"],
        'lesson_examples': [
            "This book is more interesting than that one.",
            "She is the tallest student in the class.",
            "My car is faster than yours.",
            "This is the most difficult exam I've taken.",
            "He is as smart as his brother. (equal comparison)",
            "This is the best restaurant in the city. (irregular: good → best)",
            "Health is more important than money.",
            "January is the coldest month of the year.",
        ],
        'lesson_common_mistakes': [
            "❌ This is the most best film. → ✅ This is the best film. (don't combine 'most' with an irregular superlative)",
            "❌ She is more tall than me. → ✅ She is taller than me. (short adjectives use -er, not 'more')",
            "❌ She is the smartest of the two. → ✅ She is smarter than her sister. (only two things = comparative, not superlative)",
            "❌ This is more good. → ✅ This is better.",
        ],
        'questions': [
            ('multiple_choice', "This exercise is ___ than the last one.", ["easy", "easier", "more easy", "easiest"], "easier", False),
            ('fill_blank', "She is the ___ (tall) girl in her class.", [], "tallest", False),
            ('multiple_choice', "This is ___ restaurant in the city.", ["good", "better", "the best", "best"], "the best", False),
            ('fill_blank', "Health is ___ (important) than money.", [], "more important", False),
            ('multiple_choice', "He runs ___ than his friend.", ["fast", "faster", "more fast", "fastest"], "faster", False),
            ('drag_drop', "Put the words in order.", ["brother", "my", "than", "am", "older", "I"], "I am older than my brother", False),
            ('fill_blank', "This is the ___ (expensive) phone in the shop.", [], "most expensive", False),
            ('multiple_choice', "My house is ___ than yours.", ["big", "bigger", "more big", "biggest"], "bigger", False),
            ('fill_blank', "She sings ___ (beautifully) than her sister.", [], "more beautifully", False),
            ('multiple_choice', "This is ___ day of my life.", ["happy", "happier", "the happiest", "more happy"], "the happiest", False),
            ('drag_drop', "Put the words in order.", ["Everest", "is", "the", "highest", "mountain", "in", "the", "world"], "Everest is the highest mountain in the world", False),
            ('fill_blank', "This test was ___ (difficult) than I expected.", [], "more difficult", False),
            ('multiple_choice', "She is as ___ as her mother.", ["tall", "taller", "tallest", "more tall"], "tall", False),
            ('fill_blank', "He is the ___ (intelligent) student in school.", [], "most intelligent", False),
            ('multiple_choice', "This road is ___ than that one.", ["narrow", "narrower", "more narrow", "narrowest"], "narrower", False),
            ('drag_drop', "Put the words in order.", ["of", "all", "the", "is", "she", "kindest", "the", "students"], "She is the kindest of all the students", False),
            ('fill_blank', "January is ___ (cold) month of the year.", [], "the coldest", False),
            ('multiple_choice', "Choose the correct superlative:", ["This is the most best film.", "This is the bestest film.", "This is the best film.", "This is more best film."], "This is the best film.", True),
            ('fill_blank', "This is by far ___ (good) decision you've ever made.", [], "the best", True),
            ('multiple_choice', "Which sentence correctly compares two things?", ["She is the smartest of the two.", "She is smarter than her sister.", "She is most smart than her sister.", "She is smartest than her sister."], "She is smarter than her sister.", True),
        ],
    },
    {
        'name': "Countable & Uncountable Nouns", 'icon': "🧺",
        'description': "Some, any, much, many, a few, a little.",
        'lesson_rule': "Countable nouns have singular/plural forms and can follow numbers (one "
                        "book, two books) — use 'many', 'a few' with them. Uncountable nouns have "
                        "no plural and can't follow a number directly (water, money, information, "
                        "advice) — use 'much', 'a little' with them. 'Some' is used in positive "
                        "sentences and polite offers; 'any' is used in questions and negative "
                        "sentences.",
        'lesson_structure': "Countable: many / a few / how many + plural noun. Uncountable: much / "
                             "a little / how much + singular (uncountable) noun. Both: some "
                             "(positive/offers), any (questions/negatives).",
        'lesson_signal_words': ["many, a few, how many (countable)", "much, a little, how much "
                                 "(uncountable)", "some (offers, positives)", "any (questions, "
                                 "negatives)"],
        'lesson_examples': [
            "There are many books on the shelf. (countable)",
            "There isn't much time left. (uncountable)",
            "Would you like some tea? (offer)",
            "I don't have any money. (negative)",
            "She has a few friends here. (countable, small number)",
            "We need a little sugar for the cake. (uncountable, small amount)",
            "How many people came to the party?",
            "How much water do you drink a day?",
        ],
        'lesson_common_mistakes': [
            "❌ How much apples do you want? → ✅ How many apples do you want? (apples = countable)",
            "❌ There is many traffic today. → ✅ There is much traffic today. (traffic = uncountable)",
            "❌ I have some informations. → ✅ I have some information. (information has no plural form)",
            "❌ Can I have some money? (in a negative context) → ✅ I don't have any money.",
        ],
        'questions': [
            ('multiple_choice', "There ___ some milk in the fridge.", ["is", "are", "be", "were"], "is", False),
            ('fill_blank', "How ___ (much/many) apples do you want?", [], "many", False),
            ('multiple_choice', "I don't have ___ money with me.", ["some", "any", "much", "many"], "any", False),
            ('fill_blank', "There isn't ___ (much/many) sugar left.", [], "much", False),
            ('multiple_choice', "Would you like ___ coffee?", ["some", "any", "much", "many"], "some", False),
            ('drag_drop', "Put the words in order.", ["books", "many", "has", "she", "how"], "How many books has she", False),
            ('fill_blank', "We have ___ (a few/a little) time before the train leaves.", [], "a little", False),
            ('multiple_choice', "There are ___ people in the park today.", ["much", "many", "a little", "any"], "many", False),
            ('fill_blank', "I need ___ (some/any) advice about this.", [], "some", False),
            ('multiple_choice', "There isn't ___ water in the bottle.", ["many", "much", "a few", "some"], "much", False),
            ('drag_drop', "Put the words in order.", ["friends", "has", "few", "he", "a"], "He has a few friends", False),
            ('fill_blank', "She has ___ (a few) cousins living abroad.", [], "a few", False),
            ('multiple_choice', "How ___ time do we have left?", ["many", "much", "a few", "some"], "much", False),
            ('fill_blank', "There are ___ (some/any) mistakes in this report.", [], "some", False),
            ('multiple_choice', "I have too ___ homework tonight.", ["many", "much", "a few", "some"], "much", False),
            ('drag_drop', "Put the words in order.", ["eggs", "are", "there", "any", "not"], "There are not any eggs", False),
            ('fill_blank', "Can I have ___ (some/any) more tea, please?", [], "some", False),
            ('multiple_choice', "Choose the correct sentence:", ["There is many traffic today.", "There is much traffic today.", "There are much traffic today.", "There much traffic today."], "There is much traffic today.", True),
            ('fill_blank', "There are ___ (a few) chairs missing from the room.", [], "a few", True),
            ('multiple_choice', "Which noun is uncountable?", ["chair", "information", "apple", "book"], "information", True),
        ],
    },
    {
        'name': "Modal Verbs", 'icon': "🔑",
        'description': "Can, could, must, should, might and may.",
        'lesson_rule': "Modal verbs add meaning to the main verb — ability (can/could), permission "
                        "(can/may), obligation (must/have to), advice (should), and possibility "
                        "(might/may/could) — and they never change form or take -s, don't, or "
                        "'to' before the next verb.",
        'lesson_structure': "Subject + modal + base verb (no 'to', no -s). Negative: modal + not. "
                             "Question: modal + subject + base verb?",
        'lesson_signal_words': ["can/could (ability, permission)", "must/have to (obligation)",
                                 "should (advice)", "might/may/could (possibility)",
                                 "mustn't (prohibition)"],
        'lesson_examples': [
            "She can speak French. (ability)",
            "May I come in? (permission)",
            "You must wear a seatbelt. (obligation)",
            "You mustn't smoke here. (prohibition)",
            "You should see a doctor. (advice)",
            "It might rain later. (possibility)",
            "He must be tired — he's been working all day. (logical deduction)",
            "You don't have to come if you're busy. (no obligation)",
        ],
        'lesson_common_mistakes': [
            "❌ She can to swim. → ✅ She can swim. (no 'to' after modal verbs)",
            "❌ He musts leave. → ✅ He must leave. (modals never take -s)",
            "❌ You mustn't come if you're busy. → ✅ You don't have to come if you're busy. (mustn't = prohibited, not 'no obligation')",
            "❌ Does she can swim? → ✅ Can she swim? (don't use 'does' with modal verbs)",
        ],
        'questions': [
            ('multiple_choice', "You ___ smoke in here — it's forbidden.", ["must", "mustn't", "can", "could"], "mustn't", False),
            ('fill_blank', "___ I open the window? (asking permission)", [], "Can", False),
            ('multiple_choice', "It ___ rain later, take an umbrella.", ["might", "must", "mustn't", "can"], "might", False),
            ('fill_blank', "You ___ apologize to her. (giving advice)", [], "should", False),
            ('multiple_choice', "___ you help me with this bag?", ["Could", "Must", "Should", "Mustn't"], "Could", False),
            ('fill_blank', "Students ___ wear a uniform at this school. (obligation)", [], "have to", False),
            ('multiple_choice', "He ___ speak three languages fluently.", ["can", "must", "should", "mustn't"], "can", False),
            ('drag_drop', "Put the words in order.", ["leave", "now", "you", "must"], "You must leave now", False),
            ('fill_blank', "You ___ come if you're busy. (no obligation)", [], "don't have to", False),
            ('multiple_choice', "___ I suggest a different plan?", ["May", "Must", "Mustn't", "Should"], "May", False),
            ('fill_blank', "We ___ waste food. (advice against)", [], "shouldn't", False),
            ('multiple_choice', "You ___ have told me earlier!", ["should", "can", "might", "must"], "should", False),
            ('multiple_choice', "___ you swim when you were five?", ["Can", "Could", "Must", "Should"], "Could", False),
            ('fill_blank', "You ___ (need not) bring anything; we have everything.", [], "don't need to", False),
            ('multiple_choice', "She ___ be tired after that long flight.", ["must", "mustn't", "can", "could"], "must", False),
            ('drag_drop', "Put the words in order.", ["help", "I", "you", "can"], "I can help you", False),
            ('fill_blank', "___ I ask you a personal question?", [], "May", False),
            ('multiple_choice', "Which sentence expresses strong obligation?", ["You might come.", "You must come.", "You could come.", "You may come."], "You must come.", True),
            ('fill_blank', "If it's urgent, you ___ call me immediately. (strong obligation)", [], "must", True),
            ('multiple_choice', "Which sentence shows a logical deduction?", ["He might be at home.", "He must be at home — his car is here.", "He can be at home.", "He should be at home."], "He must be at home — his car is here.", True),
        ],
    },
    {
        'name': "Question Formation", 'icon': "❓",
        'description': "Wh-questions: what, where, when, who, why, how.",
        'lesson_rule': "Wh-questions (what, where, when, who, why, how, which, whose) ask for "
                        "specific information. The word order is: question word + auxiliary verb "
                        "(do/does/did/is/are/have) + subject + main verb. If there's no other "
                        "auxiliary in the sentence, add do/does (present) or did (past).",
        'lesson_structure': "Question word + auxiliary + subject + base verb + ...? (e.g., Where "
                             "do you live?) — If 'who' or 'what' is the SUBJECT of the sentence, no "
                             "auxiliary is needed: Who called you?",
        'lesson_signal_words': ["what (thing)", "where (place)", "when (time)", "who (person)",
                                 "why (reason)", "how (manner/degree)", "which (choice)",
                                 "whose (possession)"],
        'lesson_examples': [
            "Where do you live?",
            "What is she doing?",
            "When did they arrive?",
            "Why is he crying?",
            "How much does this cost?",
            "Which movie do you prefer?",
            "Whose bag is this?",
            "Who called you? (who is the subject, no auxiliary needed)",
        ],
        'lesson_common_mistakes': [
            "❌ Where you live? → ✅ Where do you live? (need the auxiliary 'do')",
            "❌ What means this word? → ✅ What does this word mean?",
            "❌ Why he didn't come? → ✅ Why didn't he come? (auxiliary before subject)",
            "❌ How you feel today? → ✅ How do you feel today?",
        ],
        'questions': [
            ('multiple_choice', "___ do you live?", ["What", "Where", "Who", "Why"], "Where", False),
            ('fill_blank', "___ (you/do) at the weekend? (usually)", [], "What do you do", False),
            ('multiple_choice', "___ is that man over there?", ["What", "Who", "Where", "When"], "Who", False),
            ('fill_blank', "___ (you/get) to school? (habitual)", [], "How do you get", False),
            ('multiple_choice', "___ did you arrive at the airport?", ["What", "When", "Who", "Whose"], "When", False),
            ('drag_drop', "Put the words in order.", ["is", "this", "whose", "bag"], "Whose bag is this", False),
            ('fill_blank', "___ (you/feel) today?", [], "How do you feel", False),
            ('multiple_choice', "___ does this word mean?", ["What", "Who", "Where", "Whose"], "What", False),
            ('fill_blank', "___ (they/not/come) to the party?", [], "Why didn't they come", False),
            ('multiple_choice', "___ much does this jacket cost?", ["What", "How", "Why", "Which"], "How", False),
            ('drag_drop', "Put the words in order.", ["you", "movie", "which", "prefer", "do"], "Which movie do you prefer", False),
            ('fill_blank', "___ (be/the meeting)?", [], "When is the meeting", False),
            ('multiple_choice', "___ book is this — yours or mine?", ["What", "Which", "Who", "Whose"], "Which", False),
            ('fill_blank', "___ (you/get) to work every day?", [], "How do you get", False),
            ('multiple_choice', "___ is your birthday?", ["What", "When", "Where", "Who"], "When", False),
            ('drag_drop', "Put the words in order.", ["did", "you", "why", "leave", "early"], "Why did you leave early", False),
            ('fill_blank', "___ (this/belong) to?", [], "Who does this belong", False),
            ('multiple_choice', "Choose the correctly formed question:", ["Where you live?", "Where do you live?", "Where you do live?", "Where does you live?"], "Where do you live?", True),
            ('fill_blank', "___ (be/your/parents) from?", [], "Where are your parents", True),
            ('multiple_choice', "Which word asks about a reason?", ["How", "Why", "When", "Whose"], "Why", True),
        ],
    },
    {
        'name': "Conditionals & Passive Voice", 'icon': "⚡",
        'description': "If-clauses and the passive voice.",
        'lesson_rule': "Conditional sentences with 'if' describe cause and effect. The zero/first "
                        "conditional (if + present, will + base verb) describes real or likely "
                        "situations. The second conditional (if + past simple, would + base verb) "
                        "describes unreal/hypothetical present situations. The third conditional "
                        "(if + past perfect, would have + past participle) describes an unreal "
                        "past that can't be changed. The passive voice (be + past participle) "
                        "focuses on the action or the receiver rather than who did it.",
        'lesson_structure': "1st: If + present simple, will + base verb. 2nd: If + past simple, "
                             "would + base verb. 3rd: If + past perfect, would have + past "
                             "participle. Passive: subject + be (am/is/are/was/were) + past "
                             "participle (+ by agent).",
        'lesson_signal_words': ["if (condition)", "will (real future result)", "would (unreal/"
                                 "hypothetical result)", "would have (unreal past result)",
                                 "by (passive agent)"],
        'lesson_examples': [
            "If it rains, we will stay home. (1st conditional — real possibility)",
            "If I were rich, I would travel the world. (2nd conditional — unreal present)",
            "If I had studied harder, I would have passed. (3rd conditional — unreal past)",
            "The letter was sent yesterday. (passive, past)",
            "English is spoken in many countries. (passive, present)",
            "The cake was eaten by the children. (passive with agent)",
            "A new bridge is being built in the city. (passive, continuous)",
            "If you heat ice, it melts. (zero conditional — general truth)",
        ],
        'lesson_common_mistakes': [
            "❌ If I will have time, I will call you. → ✅ If I have time, I will call you. (no 'will' after 'if' in the 1st conditional)",
            "❌ If I was you, I would apologize. → ✅ If I were you... (use 'were' for all subjects in the 2nd conditional)",
            "❌ The letter sent yesterday. → ✅ The letter was sent yesterday. (need a form of 'be' in the passive)",
            "❌ English speaks in many countries. → ✅ English is spoken in many countries.",
        ],
        'questions': [
            ('multiple_choice', "If it rains, we ___ stay home.", ["will", "would", "stay", "stayed"], "will", False),
            ('fill_blank', "If I ___ (be) you, I would apologize.", [], "were", False),
            ('multiple_choice', "If she studies hard, she ___ pass the exam.", ["will", "would", "passed", "pass"], "will", False),
            ('fill_blank', "If I had known, I ___ (help) you.", [], "would have helped", False),
            ('multiple_choice', "The letter ___ sent yesterday.", ["was", "is", "has", "did"], "was", False),
            ('fill_blank', "English ___ (speak) all over the world.", [], "is spoken", False),
            ('multiple_choice', "This house ___ built in 1990.", ["was", "is", "has", "did"], "was", False),
            ('drag_drop', "Put the words in order.", ["world", "around", "the", "spoken", "is", "english"], "English is spoken around the world", False),
            ('fill_blank', "If you heat ice, it ___ (melt).", [], "melts", False),
            ('multiple_choice', "The cake ___ eaten by the children.", ["was", "is", "were", "has"], "was", False),
            ('fill_blank', "If we ___ (leave) now, we will catch the train.", [], "leave", False),
            ('multiple_choice', "A new bridge ___ being built in the city.", ["is", "was", "has", "are"], "is", False),
            ('multiple_choice', "If I have time tomorrow, I ___ visit you.", ["will", "would", "visited", "visit"], "will", False),
            ('fill_blank', "If she ___ (not/be) so busy, she would come.", [], "weren't", False),
            ('multiple_choice', "The windows ___ cleaned every week.", ["are", "is", "was", "be"], "are", False),
            ('drag_drop', "Put the words in order.", ["him", "invited", "party", "was", "to", "the"], "He was invited to the party", False),
            ('fill_blank', "If it ___ (snow) tomorrow, schools will close.", [], "snows", False),
            ('fill_blank', "If I ___ (win) the lottery, I would travel the world.", [], "won", True),
            ('multiple_choice', "Choose the correct passive sentence:", ["Someone stole my bike.", "My bike was stolen.", "My bike stole.", "My bike has steal."], "My bike was stolen.", True),
            ('fill_blank', "If I ___ (study) harder last year, I would have passed the exam.", [], "had studied", True),
        ],
    },
    {
        'name': "Reported Speech", 'icon': "🗣️",
        'description': "Turning direct speech into reported speech.",
        'lesson_rule': "When we report what someone said, we usually shift the tense one step back "
                        "into the past (backshift): present becomes past, past becomes past "
                        "perfect, and 'will' becomes 'would'. Pronouns and time/place expressions "
                        "also change to match the new speaker's perspective (today → that day, "
                        "tomorrow → the next day, here → there).",
        'lesson_structure': 'Direct: "I am tired," she said. → Reported: She said (that) she was '
                             "tired. Present Simple → Past Simple; Present Continuous → Past "
                             "Continuous; Past Simple → Past Perfect; will → would; can → could; "
                             "must → had to.",
        'lesson_signal_words': ["today → that day", "tomorrow → the next day",
                                 "yesterday → the day before", "here → there", "this → that",
                                 "now → then"],
        'lesson_examples': [
            '"I am tired," she said. -> She said she was tired.',
            '"I will call you," he said. -> He said he would call me.',
            '"I have finished," she said. -> She said she had finished.',
            '"I saw him yesterday," she said. -> She said she had seen him the day before.',
            '"I can swim," he said. -> He said he could swim.',
            '"I am reading a book," she said. -> She said she was reading a book.',
            '"I will not come," he said. -> He said he would not come.',
            '"I must leave now," he said. -> He said he had to leave then.',
        ],
        'lesson_common_mistakes': [
            "❌ She said she is tired. → ✅ She said she was tired. (backshift the tense)",
            "❌ He said he will help. → ✅ He said he would help.",
            "❌ She said she has finished. → ✅ She said she had finished.",
            "❌ He said he can swim yesterday. → ✅ He said he could swim. (don't mix present and past forms)",
        ],
        'questions': [
            ('multiple_choice', 'She said, "I am happy." -> She said she ___ happy.', ["is", "was", "has been", "be"], "was", False),
            ('fill_blank', 'He said, "I will help you." -> He said he ___ (help) me.', [], "would help", False),
            ('multiple_choice', 'He said, "I am working." -> He said he ___ working.', ["is", "was", "has been", "were"], "was", False),
            ('fill_blank', 'She said, "I have lost my keys." -> She said she ___ (lose) her keys.', [], "had lost", False),
            ('multiple_choice', 'He said, "I saw her yesterday." -> He said he ___ her the day before.', ["saw", "sees", "had seen", "has seen"], "had seen", False),
            ('drag_drop', "Put the words in order.", ["tired", "said", "was", "she", "she"], "She said she was tired", False),
            ('fill_blank', 'He said, "I can swim." -> He said he ___ (can) swim.', [], "could", False),
            ('multiple_choice', 'She said, "I don\'t like coffee." -> She said she ___ like coffee.', ["doesn't", "didn't", "isn't", "wasn't"], "didn't", False),
            ('fill_blank', 'She said, "I am going to Paris." -> She said she ___ (go) to Paris.', [], "was going", False),
            ('multiple_choice', 'He said, "I will call you tomorrow." -> He said he would call me ___.', ["tomorrow", "the next day", "yesterday", "today"], "the next day", False),
            ('drag_drop', "Put the words in order.", ["help", "said", "would", "he", "me", "he"], "He said he would help me", False),
            ('fill_blank', 'He said, "I must leave now." -> He said he ___ (must) leave then.', [], "had to", False),
            ('multiple_choice', 'She said, "I have never been to Japan." -> She said she ___ never been to Japan.', ["has", "had", "was", "is"], "had", False),
            ('fill_blank', 'She said, "I am reading a book." -> She said she ___ (read) a book.', [], "was reading", False),
            ('multiple_choice', 'He said, "I bought a car." -> He said he ___ a car.', ["buys", "bought", "had bought", "has bought"], "had bought", False),
            ('drag_drop', "Put the words in order.", ["there", "said", "she", "been", "had"], "She said she had been there", False),
            ('fill_blank', 'He said, "I will not come." -> He said he ___ (not/come).', [], "would not come", False),
            ('multiple_choice', 'Choose the correct reported sentence for: "I am cooking dinner," she said.', ["She said she is cooking dinner.", "She said she was cooking dinner.", "She said she has cooked dinner.", "She said she cook dinner."], "She said she was cooking dinner.", True),
            ('fill_blank', '"I had already left," he said. -> He said he ___ (already/leave).', [], "had already left", True),
            ('multiple_choice', "Which tense shift is correct for reported speech?", ["Present Simple stays Present Simple", "Present Simple becomes Past Simple", "Past Simple becomes Present Perfect", "Future stays Future"], "Present Simple becomes Past Simple", True),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed Grammar Battle topics and questions."

    def handle(self, *args, **options):
        topics_created = 0
        questions_created = 0

        for order, topic_data in enumerate(TOPICS, start=1):
            # Keyed by name (not order) so re-running this command after topics have been
            # reordered/expanded never mixes one topic's questions into another's row.
            topic, was_created = GrammarTopic.objects.get_or_create(
                name=topic_data['name'],
                defaults={
                    'order': order, 'icon': topic_data['icon'],
                    'description': topic_data['description'],
                    'lesson_rule': topic_data['lesson_rule'],
                    'lesson_structure': topic_data.get('lesson_structure', ''),
                    'lesson_signal_words': topic_data.get('lesson_signal_words', []),
                    'lesson_examples': topic_data['lesson_examples'],
                    'lesson_common_mistakes': topic_data.get('lesson_common_mistakes', []),
                },
            )
            if was_created:
                topics_created += 1
            else:
                # Backfill/refresh content on already-existing topics (e.g. lesson fields
                # added after the topic was first seeded).
                topic.order = order
                topic.icon = topic_data['icon']
                topic.description = topic_data['description']
                topic.lesson_rule = topic_data['lesson_rule']
                topic.lesson_structure = topic_data.get('lesson_structure', '')
                topic.lesson_signal_words = topic_data.get('lesson_signal_words', [])
                topic.lesson_examples = topic_data['lesson_examples']
                topic.lesson_common_mistakes = topic_data.get('lesson_common_mistakes', [])
                topic.save()

            for question_type, prompt, options, correct_answer, is_boss in topic_data['questions']:
                _, q_created = GrammarQuestion.objects.get_or_create(
                    topic=topic, prompt=prompt, correct_answer=correct_answer,
                    defaults={
                        'question_type': question_type, 'options': options,
                        'is_boss': is_boss,
                    },
                )
                if q_created:
                    questions_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {topics_created} new topics and {questions_created} new questions "
            f"({GrammarTopic.objects.count()} topics, {GrammarQuestion.objects.count()} questions total)."
        ))
