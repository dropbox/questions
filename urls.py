from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'questions.views.index'),
    url(r'^questions/$', 'questions.views.index'),
    url(r'^questions/orphans$', 'questions.views.view_orphans'),

    url(r'^question/add/$', 'questions.views.add_question'),
    url(r'^question/(?P<question_id>\d+)$', 'questions.views.view_question'),
    url(r'^question/(?P<question_id>\d+)/edit$', 'questions.views.edit_question'),
    url(r'^question/(?P<question_id>\d+)/delete$', 'questions.views.delete_question'),
    url(r'^question/(?P<question_id>\d+)/revisions$', 'questions.views.view_revisions'),
    url(r'^question/(?P<question_id>\d+)/status/(?P<status>(Banned|Pending|Approved))$',
        'questions.views.set_status'),
    url(r'^question/(?P<question_id>\d+)/set_revision/(?P<revision_id>\d+)$',
        'questions.views.set_revision'),

    url(r'^tag/(?P<tagname>[\w ]+)$', 'questions.views.view_tag'),
    url(r'^tags_ajax$', 'questions.views.tags_ajax'),


    url(r'users', 'questions.views.users'),

    url(r'help', 'questions.views.help'),

    url(r'^group/add/$', 'questions.views.add_group'),
    url(r'^groups/$', 'questions.views.groups'),
    url(r'^group/(?P<group_id>\d+)$', 'questions.views.view_group'),
    url(r'^group/(?P<group_id>\d+)/edit$', 'questions.views.edit_group'),
    url(r'^group/(?P<group_id>\d+)/delete$', 'questions.views.delete_group'),

    url(r'^settings/$', 'questions.views.settings'),
    url(r'^settings/edit$', 'questions.views.edit_settings'),

    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/',}, name='logout'),
    (r'^openid/', include('django_openid_auth.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
