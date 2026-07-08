from django.core.management.base import BaseCommand
from gamification.models import SurvivalScenario, SurvivalNode, SurvivalChoice

# Each scenario: name, icon, description, nodes (dict of node_key -> node data)
# Each node: npc_line, is_start, is_ending, ending_quality, choices
# Each choice: (text, quality, feedback, next_key)
SCENARIOS = [
    {
        'name': "Airport", 'icon': '✈️',
        'description': "Check in for your flight and get through to your gate.",
        'nodes': {
            'start': {
                'npc_line': "Good morning! Can I see your passport and ticket, please?",
                'is_start': True,
                'choices': [
                    ("Here you are.", 'good', "Perfect — polite and natural way to hand something over.", 'node2'),
                    ("Here.", 'ok', "It works, but 'Here you are' sounds more polite.", 'node2'),
                    ("Yes.", 'bad', "This doesn't actually give them what they asked for — you need to hand over the documents.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "Sorry, I still need to see your documents, please.",
                'choices': [
                    ("Oh, sorry! Here you are.", 'good', "Nice recovery — polite and clear.", 'node2'),
                    ("Fine, here.", 'bad', "Still a bit rude — try apologizing and handing them over politely.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Thank you. Would you like a window or an aisle seat?",
                'choices': [
                    ("A window seat, please, if it's available.", 'good', "Excellent — polite, clear, and natural.", 'ending_good'),
                    ("Window.", 'ok', "Understandable, but a full sentence sounds more natural here.", 'ending_neutral'),
                    ("I don't care.", 'bad', "This can come across as rude in a service setting — even 'either is fine' sounds warmer.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, here's your boarding pass. Have a wonderful flight!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, here's your boarding pass. Security is that way.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Alright. Here's your boarding pass.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Restaurant", 'icon': '🍽️',
        'description': "Order a meal politely and naturally at a restaurant.",
        'nodes': {
            'start': {
                'npc_line': "Good evening! Are you ready to order, or do you need more time?",
                'is_start': True,
                'choices': [
                    ("Yes, I'd like the grilled salmon, please.", 'good', "Clear and polite ordering.", 'node2'),
                    ("Salmon.", 'ok', "Understood, but adding 'I'd like... please' sounds more natural.", 'node2'),
                    ("Whatever.", 'bad', "This isn't helpful for the waiter — you need to name a dish.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "I'm sorry, could you tell me which dish you'd like?",
                'choices': [
                    ("Sorry, I'll have the grilled salmon, please.", 'good', "Good — clear and polite.", 'node2'),
                    ("Just bring me something.", 'bad', "Still vague — try naming an actual dish from the menu.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Great choice! Anything to drink?",
                'choices': [
                    ("Just water, please, thank you.", 'good', "Polite and complete — great job!", 'ending_good'),
                    ("Water.", 'ok', "Fine, but 'please' makes it sound warmer.", 'ending_neutral'),
                    ("No.", 'bad', "A bit blunt — 'No, thank you' is the polite version.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Wonderful, I'll bring that right out for you!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, coming right up.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Sure.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Hotel", 'icon': '🏨',
        'description': "Check in to your hotel room and get settled in.",
        'nodes': {
            'start': {
                'npc_line': "Welcome! Do you have a reservation with us?",
                'is_start': True,
                'choices': [
                    ("Yes, I have a reservation under the name Aliyev.", 'good', "Great — clear and complete.", 'node2'),
                    ("Yes.", 'ok', "Correct, but giving your name helps them find your booking faster.", 'node2'),
                    ("Maybe.", 'bad', "This is confusing — the receptionist needs a clear yes or no.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "I'm sorry, could you confirm if you booked a room with us?",
                'choices': [
                    ("Sorry, yes — under the name Aliyev.", 'good', "Good recovery — clear and specific.", 'node2'),
                    ("I'm not sure.", 'bad', "Still unclear — try checking your booking confirmation and giving your name.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Found it! Would you like a wake-up call tomorrow morning?",
                'choices': [
                    ("Yes, please, at 7 AM would be great.", 'good', "Perfect — polite and specific.", 'ending_good'),
                    ("Sure, 7.", 'ok', "Understood, but a fuller sentence sounds more polite.", 'ending_neutral'),
                    ("Whatever.", 'bad', "Sounds indifferent — sharing a preferred time is more helpful and polite.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, here's your key. Enjoy your stay!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "Alright, here's your key.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...OK, here's your key, room 204.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Shopping", 'icon': '🛍️',
        'description': "Find and try on clothes at a store with the clerk's help.",
        'nodes': {
            'start': {
                'npc_line': "Hi there! Can I help you find anything?",
                'is_start': True,
                'choices': [
                    ("Yes, I'm looking for a blue jacket, medium size.", 'good', "Specific and clear — very helpful for the clerk.", 'node2'),
                    ("Just looking.", 'ok', "Perfectly fine and common, though it doesn't invite more help.", 'node2'),
                    ("No.", 'bad', "This closes the conversation abruptly — a small explanation is more polite.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "OK — just let me know if you need anything!",
                'choices': [
                    ("Actually, do you have this in a smaller size?", 'good', "Nice — you re-engaged politely.", 'node2'),
                    ("...", 'bad', "Missing a chance to get help — it's fine to ask questions while shopping.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "We have that jacket in blue and black — would you like to try one on?",
                'choices': [
                    ("Yes, I'd love to try the blue one, please.", 'good', "Great — specific and enthusiastic.", 'ending_good'),
                    ("Sure.", 'ok', "Fine, but naming the color you want is more specific and helpful.", 'ending_neutral'),
                    ("I guess.", 'bad', "Sounds unsure — a clear yes/no is more useful for the clerk.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great, the fitting room is right this way!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, follow me.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Alright, this way I guess.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Job Interview", 'icon': '💼',
        'description': "Make a great impression in an English-language job interview.",
        'nodes': {
            'start': {
                'npc_line': "Thank you for coming in today. Can you tell me a bit about yourself?",
                'is_start': True,
                'choices': [
                    ("Of course! I studied marketing and have two years of experience in digital campaigns.", 'good', "Strong, specific answer — exactly what interviewers want to hear.", 'node2'),
                    ("I'm just a normal person, nothing special.", 'ok', "A bit too modest for an interview — highlighting your skills is expected and appropriate.", 'node2'),
                    ("I don't know what to say.", 'bad', "It's better to prepare a short summary of your background, even briefly.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "That's alright, take your time — maybe start with your education or work experience?",
                'choices': [
                    ("Sure — I studied business and worked in sales for a year.", 'good', "Good — concrete and confident.", 'node2'),
                    ("...", 'bad', "In an interview, it's important to answer even if you're nervous — a short answer is better than none.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Great. Why do you want to work with our company?",
                'choices': [
                    ("I admire your focus on innovation, and I'd love to contribute my skills to that.", 'good', "Excellent — shows genuine, specific interest.", 'ending_good'),
                    ("I need a job.", 'ok', "Honest, but interviewers usually want to hear what interests you about THIS company specifically.", 'ending_neutral'),
                    ("No particular reason.", 'bad', "This suggests low motivation — showing genuine interest matters in interviews.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Wonderful answer — we'll be in touch soon!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "I see. Thanks for your time today.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Alright. We'll consider your application.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Doctor", 'icon': '🩺',
        'description': "Describe your symptoms clearly to the doctor.",
        'nodes': {
            'start': {
                'npc_line': "Good morning! What brings you in today?",
                'is_start': True,
                'choices': [
                    ("I've had a sore throat and a mild fever for two days.", 'good', "Great — specific symptoms help the doctor a lot.", 'node2'),
                    ("I feel sick.", 'ok', "Understood, but describing specific symptoms helps the doctor a lot more.", 'node2'),
                    ("I don't know.", 'bad', "Try to describe how you're feeling, even generally — it helps the doctor help you.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "That's OK — can you point to where it hurts, or describe how you feel?",
                'choices': [
                    ("My throat hurts and I feel a bit hot.", 'good', "Good — now the doctor has something to work with.", 'node2'),
                    ("...", 'bad', "Doctors need some information to help — even a simple description is useful.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "I see. Do you have any allergies to medication?",
                'choices': [
                    ("No, I don't have any allergies that I know of.", 'good', "Clear and complete — very helpful.", 'ending_good'),
                    ("No.", 'ok', "Correct and clear, though a fuller sentence sounds a little more natural here.", 'ending_neutral'),
                    ("I don't remember.", 'bad', "This is important medical information — it's worth checking your records if unsure.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, I'll prescribe something safe for you. Feel better soon!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, I'll write you a prescription.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Alright, please double check with the pharmacist about allergies.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Taxi", 'icon': '🚕',
        'description': "Tell the driver where you need to go and how.",
        'nodes': {
            'start': {
                'npc_line': "Hello! Where would you like to go?",
                'is_start': True,
                'choices': [
                    ("To the central train station, please.", 'good', "Clear, specific, and polite.", 'node2'),
                    ("Train station.", 'ok', "Clear enough, but 'please' makes requests sound more polite.", 'node2'),
                    ("Just drive.", 'bad', "The driver needs an actual destination to take you anywhere.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "Sorry, could you tell me the address or place you're headed?",
                'choices': [
                    ("Sorry! To the central train station, please.", 'good', "Good recovery — clear and polite.", 'node2'),
                    ("Anywhere is fine.", 'bad', "This doesn't help the driver — always give a specific destination.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "No problem. Do you need the fastest route or the cheapest one?",
                'choices': [
                    ("The fastest route is fine, thank you.", 'good', "Polite and clear — great job.", 'ending_good'),
                    ("Fastest.", 'ok', "Clear, but a full sentence with 'please/thank you' sounds warmer.", 'ending_neutral'),
                    ("I don't care, just go.", 'bad', "This can sound impatient — a calmer response is more pleasant for both of you.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great choice, we'll be there in fifteen minutes!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, got it.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Fine.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "University", 'icon': '🎓',
        'description': "Talk to an academic advisor about registering for classes.",
        'nodes': {
            'start': {
                'npc_line': "Hello! How can I help you today?",
                'is_start': True,
                'choices': [
                    ("Hi, I'd like to ask about registering for next semester's courses.", 'good', "Clear and direct — great start.", 'node2'),
                    ("I have a question.", 'ok', "Fine to start with, but stating your actual question sooner saves time.", 'node2'),
                    ("Nothing.", 'bad', "If you came for a reason, it helps to say what you need, even briefly.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "No worries — is there something I can help you with today?",
                'choices': [
                    ("Actually yes, I need help registering for classes.", 'good', "Good — you re-engaged and stated your need clearly.", 'node2'),
                    ("...", 'bad', "It's fine to ask for help — that's exactly what advisors are here for.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Sure! Do you know which courses you'd like to take?",
                'choices': [
                    ("Yes, I'd like to register for English Literature and Statistics.", 'good', "Specific and ready — makes the process quick.", 'ending_good'),
                    ("Not really.", 'ok', "That's OK, but bringing a list of interests would speed things up next time.", 'ending_neutral'),
                    ("You choose for me.", 'bad', "Advisors can guide you, but course choices are ultimately your decision to make.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great choices! I'll get you registered right away.", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, let's look at some options together.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...I can suggest a few things, but you'll need to decide.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Bank", 'icon': '🏦',
        'description': "Open an account and handle basic banking tasks.",
        'nodes': {
            'start': {
                'npc_line': "Hello! How can I help you today?",
                'is_start': True,
                'choices': [
                    ("Hi, I'd like to open a savings account, please.", 'good', "Clear and specific — exactly what the teller needs.", 'node2'),
                    ("I want an account.", 'ok', "Clear, but naming the account type (savings/checking) helps them assist you faster.", 'node2'),
                    ("Money stuff.", 'bad', "This is too vague — try naming what you specifically need help with.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "I'm sorry, could you tell me more specifically what you need?",
                'choices': [
                    ("Sorry — I'd like to open a savings account.", 'good', "Good recovery — clear and specific.", 'node2'),
                    ("I don't know.", 'bad', "It helps to think about what you need before visiting the bank — even a general idea works.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Sure! Do you have your ID and proof of address with you?",
                'choices': [
                    ("Yes, here they are.", 'good', "Perfect — handing over the documents while speaking is natural.", 'ending_good'),
                    ("Yes.", 'ok', "Correct, but handing over the documents while speaking sounds more natural.", 'ending_neutral'),
                    ("I forgot them.", 'bad', "Without these documents, the bank usually can't open an account — good to check requirements beforehand.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, let's get your account set up right away!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, let me take a look.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...I'm afraid you'll need to come back with those documents.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Post Office", 'icon': '📦',
        'description': "Send a package and choose the right shipping option.",
        'nodes': {
            'start': {
                'npc_line': "Good afternoon! What can I do for you?",
                'is_start': True,
                'choices': [
                    ("I'd like to send this package to Germany, please.", 'good', "Specific and complete — great request.", 'node2'),
                    ("Send this.", 'ok', "Understood, but naming the destination and using 'please' sounds more complete.", 'node2'),
                    ("Here.", 'bad', "The clerk needs to know what you want to do with the package.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "Sorry, are you sending this somewhere, or picking something up?",
                'choices': [
                    ("Sending it — to Germany, please.", 'good', "Good — clear and specific now.", 'node2'),
                    ("I don't know.", 'bad', "Try to know your task before arriving — sending, receiving, or buying stamps, for example.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Would you like standard or express shipping?",
                'choices': [
                    ("Standard is fine, thank you.", 'good', "Clear and polite — great job.", 'ending_good'),
                    ("Standard.", 'ok', "Clear, but adding 'please/thank you' sounds warmer.", 'ending_neutral'),
                    ("Whichever.", 'bad', "A clear choice helps the clerk complete your request faster.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great, that will arrive in about a week. Here's your receipt!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, here's your receipt.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...I'll just pick one for you then.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Coffee Shop", 'icon': '☕',
        'description': "Order your drink naturally at a busy coffee shop.",
        'nodes': {
            'start': {
                'npc_line': "Hi! What can I get started for you?",
                'is_start': True,
                'choices': [
                    ("I'd like a medium cappuccino, please.", 'good', "Specific and polite — perfect order.", 'node2'),
                    ("Coffee.", 'ok', "Understood, but naming the specific drink and size helps a lot.", 'node2'),
                    ("Something.", 'bad', "The barista needs to know which drink you'd like from the menu.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "Sure, would you like to look at our menu?",
                'choices': [
                    ("Yes, please — I'll have a cappuccino.", 'good', "Good — you made a clear decision.", 'node2'),
                    ("Never mind.", 'bad', "It's fine to take a moment to decide — just let them know when you're ready.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Would you like that for here or to go?",
                'choices': [
                    ("To go, please, thank you.", 'good', "Polite and complete — great job.", 'ending_good'),
                    ("To go.", 'ok', "Clear, but 'please/thank you' makes it sound more natural.", 'ending_neutral'),
                    ("Doesn't matter.", 'bad', "A quick, clear answer helps the barista serve you the right way.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, that'll be ready in just a moment!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, coming right up.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Sure, I'll just put it in a cup.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Pharmacy", 'icon': '💊',
        'description': "Describe your symptoms and get the right medicine safely.",
        'nodes': {
            'start': {
                'npc_line': "Hello! How can I help you today?",
                'is_start': True,
                'choices': [
                    ("Hi, I need something for a headache, please.", 'good', "Clear symptom description — very helpful for the pharmacist.", 'node2'),
                    ("I need medicine.", 'ok', "Understood, but describing the symptom helps the pharmacist recommend the right medicine.", 'node2'),
                    ("Give me pills.", 'bad', "This sounds demanding — describing what's wrong is more helpful and polite.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "Of course — could you tell me what symptoms you have?",
                'choices': [
                    ("Sorry, I have a bad headache.", 'good', "Good — now the pharmacist can help properly.", 'node2'),
                    ("I don't want to say.", 'bad', "Sharing your symptoms helps the pharmacist give you safe, correct advice.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Are you taking any other medication right now?",
                'choices': [
                    ("No, I'm not taking anything else.", 'good', "Clear and complete — very helpful for safety.", 'ending_good'),
                    ("No.", 'ok', "Correct and clear, though a full sentence sounds a bit more natural.", 'ending_neutral'),
                    ("I'm not sure.", 'bad', "This is important safety information — it's worth checking before buying medicine.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great, this should help. Take one every six hours.", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, this one should work for you.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Please check with your doctor first, just to be safe.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Hairdresser", 'icon': '💇',
        'description': "Explain exactly what haircut or style you want.",
        'nodes': {
            'start': {
                'npc_line': "Hi there! What are we doing today?",
                'is_start': True,
                'choices': [
                    ("I'd like a trim, just an inch off, please.", 'good', "Specific and clear — exactly what the stylist needs.", 'node2'),
                    ("A haircut.", 'ok', "Clear enough, but describing how much/what style helps the stylist a lot.", 'node2'),
                    ("Whatever.", 'bad', "Stylists usually need a clearer idea of what you want, even roughly.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "No worries — do you have a particular length or style in mind?",
                'choices': [
                    ("Just a small trim, please.", 'good', "Good — now the stylist has a clear direction.", 'node2'),
                    ("You decide.", 'bad', "This can lead to a result you don't like — sharing at least a rough idea is helpful.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Would you like your hair washed first?",
                'choices': [
                    ("Yes, please, that would be great.", 'good', "Polite and warm — great answer.", 'ending_good'),
                    ("Sure.", 'ok', "Fine, but a fuller phrase sounds more natural and polite.", 'ending_neutral'),
                    ("I don't care.", 'bad', "A clear yes/no helps the stylist plan your appointment.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, let's get you into the chair!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, this way please.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Alright, let's just get started.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Cinema", 'icon': '🎬',
        'description': "Buy movie tickets and snacks at the counter.",
        'nodes': {
            'start': {
                'npc_line': "Hi! Which movie would you like to see?",
                'is_start': True,
                'choices': [
                    ("Two tickets for the 7 PM showing, please.", 'good', "Specific and complete — perfect order.", 'node2'),
                    ("This one.", 'ok', "Understood if you're pointing, but naming the movie and time is clearer.", 'node2'),
                    ("I don't know.", 'bad', "It helps to check the showtimes before reaching the counter.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "No problem — would you like me to show you what's playing tonight?",
                'choices': [
                    ("Yes, please, that would help.", 'good', "Good — asking for help is completely fine.", 'node2'),
                    ("Forget it.", 'bad', "It's completely normal to ask for help deciding — no need to give up.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Would you like any popcorn or drinks with that?",
                'choices': [
                    ("Yes, a medium popcorn, please.", 'good', "Clear and specific — great order.", 'ending_good'),
                    ("Maybe.", 'ok', "A clear yes or no is easier for the clerk to act on.", 'ending_neutral'),
                    ("No.", 'bad', "A bit blunt — 'No, thank you' sounds more polite when declining an offer.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great, here are your tickets and popcorn — enjoy the movie!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, just tickets then. Enjoy the movie.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...Alright, here are your tickets.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Gym", 'icon': '🏋️',
        'description': "Sign up for a membership and pick the right plan.",
        'nodes': {
            'start': {
                'npc_line': "Hi! Are you interested in joining the gym?",
                'is_start': True,
                'choices': [
                    ("Yes, I'd like to sign up for a membership, please.", 'good', "Confident and clear — great start.", 'node2'),
                    ("Maybe.", 'ok', "That's fine, but sharing more interest helps the staff guide you better.", 'node2'),
                    ("Just looking.", 'bad', "That's OK, but letting them know your goals can lead to helpful suggestions.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "Sure, no pressure — would you like a quick tour of the facilities?",
                'choices': [
                    ("Yes, please, I'd love that.", 'good', "Good — you re-engaged politely.", 'node2'),
                    ("No thanks, bye.", 'bad', "This ends the conversation abruptly — even declining can be done more warmly.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "Are you interested in a monthly or annual plan?",
                'choices': [
                    ("The monthly plan sounds good for now, thank you.", 'good', "Clear, polite, and decisive — great job.", 'ending_good'),
                    ("Monthly.", 'ok', "Clear, but a fuller sentence with 'thank you' sounds warmer.", 'ending_neutral'),
                    ("Doesn't matter.", 'bad', "This decision affects your payments — it's worth giving a clear answer.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Great choice! Let's get you signed up.", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, I'll set that up for you.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...I'll just put you on the standard plan then.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
    {
        'name': "Real Estate", 'icon': '🏠',
        'description': "Talk to an agent about renting an apartment.",
        'nodes': {
            'start': {
                'npc_line': "Hello! Are you looking to rent or buy?",
                'is_start': True,
                'choices': [
                    ("I'm looking to rent a two-bedroom apartment, please.", 'good', "Specific and clear — very helpful for the agent.", 'node2'),
                    ("Rent.", 'ok', "Clear, but adding details like the number of bedrooms helps a lot.", 'node2'),
                    ("I don't know.", 'bad', "It helps to have a general idea — renting, buying, budget, size — before meeting an agent.", 'recover'),
                ],
            },
            'recover': {
                'npc_line': "That's alright — are you thinking of renting or buying for now?",
                'choices': [
                    ("Renting, I think — maybe a one or two-bedroom place.", 'good', "Good — a general idea is a great start.", 'node2'),
                    ("I'll figure it out myself.", 'bad', "Agents are there to help — it's fine to think out loud with them.", 'ending_bad'),
                ],
            },
            'node2': {
                'npc_line': "What's your budget per month, roughly?",
                'choices': [
                    ("Around 500 dollars a month would be ideal.", 'good', "Specific and useful — makes the search much easier.", 'ending_good'),
                    ("Not too much.", 'ok', "Giving a rough number helps the agent find better matches faster.", 'ending_neutral'),
                    ("I don't want to say.", 'bad', "Sharing a budget range helps agents avoid wasting your time on unsuitable places.", 'ending_bad'),
                ],
            },
            'ending_good': {'npc_line': "Perfect, I have a few great options in that range!", 'is_ending': True, 'ending_quality': 'good'},
            'ending_neutral': {'npc_line': "OK, let me see what's available.", 'is_ending': True, 'ending_quality': 'neutral'},
            'ending_bad': {'npc_line': "...I'll show you a general list, then.", 'is_ending': True, 'ending_quality': 'bad'},
        },
    },
]


class Command(BaseCommand):
    help = "Seed Daily Survival Challenge scenarios, nodes and choices."

    def handle(self, *args, **options):
        scenarios_created = 0
        nodes_created = 0
        choices_created = 0

        for scenario_data in SCENARIOS:
            scenario, was_created = SurvivalScenario.objects.get_or_create(
                name=scenario_data['name'],
                defaults={'icon': scenario_data['icon'], 'description': scenario_data['description']},
            )
            if was_created:
                scenarios_created += 1
            else:
                scenario.icon = scenario_data['icon']
                scenario.description = scenario_data['description']
                scenario.save()

            # First pass: create/update all nodes (without choices) so next_node FKs can resolve.
            node_objs = {}
            for node_key, node_data in scenario_data['nodes'].items():
                node, n_created = SurvivalNode.objects.get_or_create(
                    scenario=scenario, node_key=node_key,
                    defaults={
                        'npc_line': node_data['npc_line'],
                        'is_start': node_data.get('is_start', False),
                        'is_ending': node_data.get('is_ending', False),
                        'ending_quality': node_data.get('ending_quality', ''),
                    },
                )
                if not n_created:
                    node.npc_line = node_data['npc_line']
                    node.is_start = node_data.get('is_start', False)
                    node.is_ending = node_data.get('is_ending', False)
                    node.ending_quality = node_data.get('ending_quality', '')
                    node.save()
                else:
                    nodes_created += 1
                node_objs[node_key] = node

            # Second pass: create/update choices now that every node in this scenario exists.
            for node_key, node_data in scenario_data['nodes'].items():
                node = node_objs[node_key]
                for text, quality, feedback, next_key in node_data.get('choices', []):
                    _, c_created = SurvivalChoice.objects.get_or_create(
                        node=node, choice_text=text,
                        defaults={
                            'quality': quality, 'feedback': feedback,
                            'next_node': node_objs[next_key],
                        },
                    )
                    if c_created:
                        choices_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {scenarios_created} new scenarios, {nodes_created} new nodes, "
            f"{choices_created} new choices ({SurvivalScenario.objects.count()} scenarios, "
            f"{SurvivalNode.objects.count()} nodes, {SurvivalChoice.objects.count()} choices total)."
        ))
