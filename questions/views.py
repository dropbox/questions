from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


from shortcuts import r2r, json_response
from models import Group, Question, QuestionRevision, Settings
from forms import QuestionForm, GroupForm, SettingsForm

from tagging.models import Tag, TaggedItem

import operator

@login_required
def index(request):
    context = {}
    approved_questions = Question.objects.filter(status__exact="Approved")
    pending_questions = Question.objects.filter(status__exact="Pending")
    banned_questions = Question.objects.filter(status__exact="Banned")

    settings = Settings.get_by_user(request.user)
    if settings.group:
        approved_questions = approved_questions.filter(groups__id=settings.group.id)
        pending_questions = pending_questions.filter(groups__id=settings.group.id)
        banned_questions = banned_questions.filter(groups__id=settings.group.id)

    context["approved_questions"] = approved_questions
    context["pending_questions"] = pending_questions
    context["banned_questions"] = banned_questions
    context["settings"] = settings
    return r2r(request, "index", context)


@login_required
def view_orphans(request):
    context = {}

    approved_questions = Question.objects.filter(status__exact="Approved", groups=None)
    pending_questions = Question.objects.filter(status__exact="Pending", groups=None)
    banned_questions = Question.objects.filter(status__exact="Banned", groups=None)

    context["approved_questions"] = approved_questions
    context["pending_questions"] = pending_questions
    context["banned_questions"] = banned_questions

    return r2r(request, "view_orphans", context)


@login_required
def add_question(request):
    context = {}

    settings = Settings.get_by_user(request.user)
    initial = {}

    if settings.group:
        initial["groups"] = [settings.group.id]

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.added_by = request.user
            question.save()

            revision = QuestionRevision(
                question=question, user=request.user,
                text=form.cleaned_data["body"], active=True)
            revision.save()
            return HttpResponseRedirect("/question/%s" % question.id)
    else:
        form = QuestionForm(initial=initial)

    context["form"] = form


    return r2r(request, "add_question", context)


@login_required
def view_question(request, question_id):
    context = {
        "active_revision": True,
        "settings": Settings.get_by_user(request.user),
    }

    revision_id = request.GET.get("revision_id", None)
    question = Question.objects.get(pk=question_id)
    active_revision = question.get_active_revision()
    revision = active_revision

    if revision_id is not None and revision.id != revision_id:
        context["active_revision"] = False
        revision = QuestionRevision.objects.get(question_id=question_id, pk=revision_id)


    context["question"] = question
    context["revision"] = revision
    return r2r(request, "view_question", context)


@login_required
def set_revision(request, question_id, revision_id):
    context = {}
    question = Question.objects.get(pk=question_id)
    active_revision = question.get_active_revision()
    revision = active_revision

    if revision.id != revision_id:
        revision = QuestionRevision.objects.get(question_id=question_id, pk=revision_id)
        revision.active = True
        revision.save()

        active_revision.active=False
        active_revision.save()

    return HttpResponseRedirect("/question/%s" % question_id)


@login_required
def view_revisions(request, question_id):
    context = {}
    question = Question.objects.get(pk=question_id)
    context["question"] = question
    context["revisions"] = QuestionRevision.objects.filter(question_id=question.id).order_by('date_added')
    return r2r(request, "view_revisions", context)

@login_required
def delete_question(request, question_id):
    context = {}
    question = Question.objects.get(pk=question_id)
    if request.user.is_staff or request.user.email == question.added_by.email:
        question.delete()
    return HttpResponseRedirect("/questions")


@login_required
def edit_question(request, question_id):
    context = {}
    question = Question.objects.get(pk=question_id)
    old_revision = question.get_active_revision()

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            question = form.save()
            if old_revision.text != form.cleaned_data["body"]:
                new_revision = QuestionRevision(
                    question=question, user=request.user,
                    text=form.cleaned_data["body"], active=True)
                new_revision.save()
                old_revision.active = False
                old_revision.save()
            return HttpResponseRedirect("/question/%s" % question_id)
    else:
        form = QuestionForm(instance=question, initial={
            "body": old_revision.text
        })

    context["form"] = form
    return r2r(request, "edit_question", context)


@login_required
def set_status(request, question_id, status):
    question = Question.objects.get(pk=question_id)
    if question.status != status:
        question.status = status
        question.save()
    return HttpResponseRedirect("/question/%s" % question_id)


@login_required
def add_group(request):
    context = {}

    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.added_by = request.user
            group.save()
            return HttpResponseRedirect("/group/%s" % group.id)
    else:
        form = GroupForm()

    context["form"] = form
    return r2r(request, "add_group", context)


@login_required
def view_group(request, group_id):
    context = {}
    context["group"] = Group.objects.get(pk=group_id)

    approved_questions = Question.objects.filter(status__exact="Approved")
    pending_questions = Question.objects.filter(status__exact="Pending")
    banned_questions = Question.objects.filter(status__exact="Banned")

    approved_questions = approved_questions.filter(groups__id=group_id)
    pending_questions = pending_questions.filter(groups__id=group_id)
    banned_questions = banned_questions.filter(groups__id=group_id)

    context["approved_questions"] = approved_questions
    context["pending_questions"] = pending_questions
    context["banned_questions"] = banned_questions
    context["settings"] = Settings.get_by_user(request.user)
    return r2r(request, "view_group", context)


@login_required
def delete_group(request, group_id):
    context = {}
    group = Group.objects.get(pk=group_id)
    if request.user.is_staff or request.user.email == group.added_by.email:
        group.delete()
    return HttpResponseRedirect("/groups")


@login_required
def edit_group(request, group_id):
    context = {}
    group = Group.objects.get(pk=group_id)

    if not request.user.is_staff and request.user.email != group.added_by.email:
        return HttpResponseRedirect("/group/%s" % group_id)

    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/group/%s" % group_id)
    else:
        form = GroupForm(instance=group)

    context["form"] = form
    return r2r(request, "edit_group", context)

@login_required
def view_tag(request, tagname):
    context = {}

    approved_questions = Question.objects.filter(status__exact="Approved")
    pending_questions = Question.objects.filter(status__exact="Pending")
    banned_questions = Question.objects.filter(status__exact="Banned")

    settings = Settings.get_by_user(request.user)
    if settings.group:
        approved_questions = approved_questions.filter(groups__id=settings.group.id)
        pending_questions = pending_questions.filter(groups__id=settings.group.id)
        banned_questions = banned_questions.filter(groups__id=settings.group.id)

    context["tagname"] = tagname
    tagname = '"%s"' % tagname
    context["approved_questions"] = TaggedItem.objects.get_by_model(approved_questions, tagname)
    context["pending_questions"] = TaggedItem.objects.get_by_model(pending_questions, tagname)
    context["banned_questions"] = TaggedItem.objects.get_by_model(banned_questions, tagname)
    context["settings"] = settings

    return r2r(request, "view_tag", context)


@login_required
def tags_ajax(request):
    term = request.GET.get("term")

    if term:
        tags = Tag.objects.filter(name__startswith=term)
    else:
        tags = Tag.objects.all()

    return json_response([tag.name for tag in tags])


@login_required
def settings(request):
    context = {}
    context["settings"] = Settings.get_by_user(request.user)
    return r2r(request, "settings", context)


@login_required
def edit_settings(request):
    context = {}
    settings = Settings.get_by_user(request.user)

    if request.method == "POST":
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/settings")
    else:
        form = SettingsForm(instance=settings)

    context["form"] = form
    return r2r(request, "edit_settings", context)


@login_required
def users(request):
    context = {}
    counts = {}

    for questions in Question.objects.all():
        email = questions.added_by.email
        if email not in counts:
            counts[email] = 0
        counts[email] += 1

    for user in User.objects.all():
        if user.email not in counts:
            counts[user.email] = 0

    # Double sort since sort is stable. Want names alpha after count
    context["counts"] = sorted(counts.items(), key=operator.itemgetter(0))
    context["counts"] = sorted(context["counts"], key=operator.itemgetter(1), reverse=True)
    return r2r(request, "users", context)


@login_required
def groups(request):
    context = {}
    context["groups"] = Group.objects.all()
    return r2r(request, "groups", context)


@login_required
def help(request):
    return r2r(request, "help")


def failure_handler(request, message, status=None, template_name=None, exception=None):
    context = {
        'allowed_domains': getattr(django_settings, "OPENID_RESTRICT_TO_DOMAINS", tuple()),
    }
    return r2r(request, "login_failed", context)
