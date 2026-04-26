from django.core.management.base import BaseCommand
from game.models import IrregularVerb

VERBS = [
    ("be", "was/were", "been"),
    ("begin", "began", "begun"),
    ("break", "broke", "broken"),
    ("bring", "brought", "brought"),
    ("build", "built", "built"),
    ("buy", "bought", "bought"),
    ("catch", "caught", "caught"),
    ("choose", "chose", "chosen"),
    ("come", "came", "come"),
    ("cost", "cost", "cost"),
    ("cut", "cut", "cut"),
    ("do", "did", "done"),
    ("draw", "drew", "drawn"),
    ("drink", "drank", "drunk"),
    ("drive", "drove", "driven"),
    ("eat", "ate", "eaten"),
    ("fall", "fell", "fallen"),
    ("feel", "felt", "felt"),
    ("find", "found", "found"),
    ("fly", "flew", "flown"),
    ("forget", "forgot", "forgotten"),
    ("get", "got", "got/gotten"),
    ("give", "gave", "given"),
    ("go", "went", "gone"),
    ("grow", "grew", "grown"),
    ("have", "had", "had"),
    ("hear", "heard", "heard"),
    ("hide", "hid", "hidden"),
    ("hit", "hit", "hit"),
    ("hold", "held", "held"),
    ("keep", "kept", "kept"),
    ("know", "knew", "known"),
    ("leave", "left", "left"),
    ("let", "let", "let"),
    ("lose", "lost", "lost"),
    ("make", "made", "made"),
    ("meet", "met", "met"),
    ("pay", "paid", "paid"),
    ("put", "put", "put"),
    ("read", "read", "read"),
    ("ride", "rode", "ridden"),
    ("ring", "rang", "rung"),
    ("run", "ran", "run"),
    ("say", "said", "said"),
    ("see", "saw", "seen"),
    ("sell", "sold", "sold"),
    ("send", "sent", "sent"),
    ("show", "showed", "shown"),
    ("sing", "sang", "sung"),
    ("sit", "sat", "sat"),
    ("sleep", "slept", "slept"),
    ("speak", "spoke", "spoken"),
    ("spend", "spent", "spent"),
    ("stand", "stood", "stood"),
    ("steal", "stole", "stolen"),
    ("swim", "swam", "swum"),
    ("take", "took", "taken"),
    ("teach", "taught", "taught"),
    ("tell", "told", "told"),
    ("think", "thought", "thought"),
    ("throw", "threw", "thrown"),
    ("understand", "understood", "understood"),
    ("wake", "woke", "woken"),
    ("wear", "wore", "worn"),
    ("win", "won", "won"),
    ("write", "wrote", "written"),
]


class Command(BaseCommand):
    help = 'Seed the database with common irregular verbs'

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0
        for base, past, pp in VERBS:
            obj, was_created = IrregularVerb.objects.get_or_create(
                base=base,
                defaults={'past': past, 'pp': pp}
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done! Created: {created} verbs, Skipped (already exist): {skipped} verbs.'
            )
        )
