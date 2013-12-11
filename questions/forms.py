from django.forms import ModelForm, ChoiceField, RadioSelect, Textarea, CharField

from models import Question, QuestionRevision, Group, Settings


class QuestionForm(ModelForm):

    body = CharField(widget=Textarea())

    class Meta:
        model = Question
        exclude = ("status", "added_by")


class GroupForm(ModelForm):
    class Meta:
        model = Group
        exclude = ("added_by", )


class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        exclude = ("user",)
