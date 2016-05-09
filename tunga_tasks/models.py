# encoding=utf8
from __future__ import unicode_literals

import re
import urllib
from _mysql import result
from urllib import urlencode

import requests
import tagulous.models
from django.db import models
from django.db.models.query_utils import Q
from dry_rest_permissions.generics import allow_staff_or_superuser

from tunga import settings
from tunga_auth.models import USER_TYPE_DEVELOPER
from tunga_profiles.models import Skill, Connection

CURRENCY_EUR = 'EUR'
CURRENCY_USD = 'USD'

CURRENCY_CHOICES = (
    (CURRENCY_EUR, 'EUR'),
    (CURRENCY_USD, 'USD')
)

VISIBILITY_DEVELOPER = 1
VISIBILITY_MY_TEAM = 2
VISIBILITY_CUSTOM = 3
VISIBILITY_ONLY_ME = 4

VISIBILITY_CHOICES = (
    (VISIBILITY_DEVELOPER, 'Developers'),
    (VISIBILITY_MY_TEAM, 'My Team'),
    (VISIBILITY_CUSTOM, 'Custom'),
    (VISIBILITY_ONLY_ME, 'Only Me')
)

TASK_REQUEST_CLOSE = 1
TASK_REQUEST_PAY = 2

TASK_REQUEST_CHOICES = (
    (TASK_REQUEST_CLOSE, 'Close Request'),
    (TASK_REQUEST_PAY, 'Payment Request')
)


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_created', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    fee = models.BigIntegerField()
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0][0])
    deadline = models.DateTimeField(blank=True, null=True)
    skills = tagulous.models.TagField(Skill)
    visibility = models.PositiveSmallIntegerField(choices=VISIBILITY_CHOICES, default=VISIBILITY_CHOICES[0][0])
    closed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    visible_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='task_invites', blank=True)
    applicants = models.ManyToManyField(
            settings.AUTH_USER_MODEL, through='Application', through_fields=('task', 'user'),
            related_name='task_applications', blank=True)
    participants = models.ManyToManyField(
            settings.AUTH_USER_MODEL, through='Participation', through_fields=('task', 'user'),
            related_name='task_participants', blank=True)
    satisfaction = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.summary

    @property
    def display_fee(self):
        currency_symbols = {'EUR': '€', 'USD': '$'}
        if self.currency in currency_symbols:
            return '%s%s' % (currency_symbols[self.currency], self.fee)
        return self.fee

    @property
    def summary(self):
        return '%s - Fee: %s' % (self.title, self.display_fee)

    def get_default_participation(self):
        tags = ['tunga.io', 'tunga']
        if self.skills:
            tags.extend(str(self.skills).split(','))
        return {
            'type': 'payment', 'language': 'EN', 'title': self.summary, 'description': self.description or self.summary,
            'keywords': tags, 'participants': [
                {'id': 'mailto:admin@tunga.io', 'role': 'owner', 'share': '10%'}
            ]
        }

    def mobbr_participation(self, check_only=False):
        participation_meta = self.get_default_participation()
        if not self.url:
            return participation_meta, False

        mobbr_info_url = '%s?url=%s' % ('https://api.mobbr.com/api_v1/uris/info', urllib.quote_plus(self.url))
        r = requests.get(mobbr_info_url, **{'headers': {'Accept': 'application/json'}})
        has_script = False
        if r.status_code == 200:
            response = r.json()
            task_script = response['result']['script']
            for meta_key in participation_meta:
                if meta_key == 'keywords':
                    if isinstance(task_script[meta_key], list):
                        participation_meta[meta_key].extend(task_script[meta_key])
                elif meta_key == 'participants':
                    if isinstance(task_script[meta_key], list):
                        absolute_shares = []
                        relative_shares = []
                        absolute_participants = []
                        relative_participants = []

                        for key, participant in enumerate(task_script[meta_key]):
                            if re.match(r'\d+%$', participant['share']):
                                share = int(participant['share'].replace("%", ""))
                                if share > 0:
                                    absolute_shares.append(share)
                                    new_participant = participant
                                    new_participant['share'] = share
                                    absolute_participants.append(new_participant)
                            else:
                                share = int(participant['share'])
                                if share > 0:
                                    relative_shares.append(share)
                                    new_participant = participant
                                    new_participant['share'] = share
                                    relative_participants.append(new_participant)

                        additional_participants = []
                        total_absolutes = sum(absolute_shares)
                        total_relatives = sum(relative_shares)
                        if total_absolutes >= 100 or total_relatives == 0:
                            additional_participants = absolute_participants
                        elif total_absolutes == 0:
                            additional_participants = relative_participants
                        else:
                            additional_participants = absolute_participants
                            for participant in relative_participants:
                                share = int(round(((participant['share']*(100-total_absolutes))/total_relatives), 0))
                                if share > 0:
                                    new_participant = participant
                                    new_participant['share'] = share
                                    additional_participants.append(new_participant)
                        if len(additional_participants):
                            participation_meta[meta_key].extend(additional_participants)
                            has_script = True
                elif task_script[meta_key]:
                    participation_meta[meta_key] = task_script[meta_key]
        return participation_meta, has_script

    @property
    def meta_participation(self):
        participation_meta, has_script = self.mobbr_participation()
        # TODO: Update local participation script to use defined shares
        if not has_script:
            participants = self.participation_set.filter(accepted=True).order_by('share')
            total_shares = 90
            num_participants = participants.count()
            for participant in participants:
                participation_meta['participants'].append(
                    {
                        'id': 'mailto:%s' % participant.user.email,
                        'role': participant.role,
                        'share': int(total_shares/num_participants)
                    }
                )
        return participation_meta

    @property
    def meta_payment(self):
        return {'task_url': '/task/%s/' % self.id, 'amount': self.fee, 'currency': self.currency}

    @property
    def skills_list(self):
        return str(self.skills)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'title', 'fee')

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        if self.has_object_write_permission(request):
            return True
        if self.visibility == VISIBILITY_DEVELOPER:
            return request.user.type == USER_TYPE_DEVELOPER
        elif self.visibility == VISIBILITY_MY_TEAM:
            return bool(
                Connection.objects.exclude(accepted=False).filter(
                    Q(from_user=self.user, to_user=request.user) | Q(from_user=request.user, to_user=self.user)
                ).count()
            )
        elif self.visibility == VISIBILITY_CUSTOM:
            return self.participation_set.filter((Q(accepted=True) | Q(responded=False)), user=request.user).count()
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user == self.user or \
               self.participation_set.filter((Q(accepted=True) | Q(responded=False)), user=request.user).count()


class Application(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s - %s' % (self.user.get_short_name() or self.user.username, self.task.title)

    class Meta:
        unique_together = ('user', 'task')


class Participation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)
    assignee = models.BooleanField(default=False)
    role = models.CharField(max_length=100, default='Developer')
    share = models.IntegerField(blank=True, null=True)
    satisfaction = models.SmallIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participants_added')
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s - %s' % (self.user.get_short_name() or self.user.username, self.task.title)

    class Meta:
        unique_together = ('user', 'task')
        verbose_name_plural = 'participation'


class TaskRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=TASK_REQUEST_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s - %s' % (self.get_type_display(), self.task.title)


class SavedTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s - %s' % (self.user.get_short_name() or self.user.username, self.task.title)
