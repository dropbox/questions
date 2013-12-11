
import json
from django.core.management.base import BaseCommand, CommandError
from questions.models import Group, Question

class Command(BaseCommand):
    help = 'Dumps Questions to JSON'

    def handle(self, *args, **options):
        data = {}

        groups = Group.objects.all()
        for group in groups:
            data[group.name] = []

            for question in group.question_set.all():
                if question.status != "Approved":
                    continue
                data[group.name].append((question.title, question.tags.split(",")))

        print json.dumps(data)
