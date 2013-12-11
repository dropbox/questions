from django.db import models
from django.contrib.auth.models import User
from djangoratings.fields import RatingField
from tagging.fields import TagField
import tagging

from shortcuts import choices

class Group(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    added_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Settings(models.Model):
    user = models.ForeignKey(User)

    group = models.ForeignKey(Group, blank=True, null=True)
    syntax_highlighting = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.email

    @classmethod
    def get_by_user(cls, user):
        try:
            settings = cls.objects.get(user_id=user.id)
        except cls.DoesNotExist:
            settings = cls(user=user)
            settings.save()
        return settings



class Question(models.Model):
    title = models.CharField(max_length=255)

    status_choices = choices(('Approved', 'Pending', 'Banned'))
    status = models.CharField(max_length=30, choices=status_choices, default="Pending")

    tags = TagField(blank=True, null=True)

    difficulty_choices = choices(("Softball", "Easy", "Medium", "Hard"))
    difficulty = models.CharField(max_length=20, choices=difficulty_choices, default="Easy")

    groups = models.ManyToManyField(Group)

    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User)

    def get_latest_revision(self):
        return QuestionRevision.objects.filter(question_id=self.id).latest('date_added')

    def get_active_revision(self):
        return QuestionRevision.objects.get(question_id=self.id, active=True)

tagging.register(Question, tag_descriptor_attr="tag_list")


class QuestionRevision(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    text = models.TextField()
    active = models.BooleanField()
    date_added = models.DateTimeField(auto_now_add=True)
