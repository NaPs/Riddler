import os
import base64
from datetime import datetime, timedelta

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Sum
from django.core.urlresolvers import reverse


def gen_random_id():
    """ Generate a 4 characters length url-safe random id.
    """
    return base64.urlsafe_b64encode(os.urandom(3))


class RichTextField(models.TextField):
    pass


class Applicant(models.Model):

    """ An applicant.
    """

    firstname = models.CharField(_('Firstname'), max_length=30)
    lastname = models.CharField(_('Lastname'), max_length=30)


    def __unicode__(self):
        return self.fullname

    @property
    def fullname(self):
        return u'%s %s' % (self.firstname, self.lastname)

    class Meta:
        verbose_name = _('applicant')
        verbose_name_plural = _('applicants')


class Series(models.Model):

    """ A serie of question on the same theme.
    """

    name = models.CharField(_('name'), max_length=150)
    instructions = RichTextField(_('Instructions'), blank=True, null=True)


    def __unicode__(self):
        env = {'name': self.name,
               'questions': self.questions,
               'duration': self.duration}
        return _(u'%(name)s (%(questions)s question(s), ~%(duration)s minutes)')  % env

    @property
    def questions(self):
        """ Number of questions that make up this series.
        """
        return self.question_set.count()

    @property
    def duration(self):
        """ Estimated time (in minutes) to answer the questions of this series.
        """
        return int(self.question_set.aggregate(Sum('typical_duration'))['typical_duration__sum'] / 60)

    def get_first_unanswered(self, test):
        """ Get the first question of the series that has never been answered
            for the provided test.

        Return None if no questions have been unanswered.
        """
        already_answered = test.answer_set.filter(end_to_answer_date__isnull=False)
        already_answered = already_answered.values_list('question__pk', flat=True)
        next_questions = self.question_set.exclude(pk__in=already_answered).order_by('pk')
        if next_questions:
            return next_questions[0]
        else:
            return None

    class Meta:
        verbose_name = _('series')
        verbose_name_plural = _('series')


class Question(models.Model):

    """ A question itself, belongs to a series.
    """

    EDITOR_MODE_CHOICES = (('python', _('Python')),
                           ('css', _('CSS')),
                           ('go', _('Go')),
                           ('htmlmixed', _('HTML')),
                           ('javascript', _('Javascript')),
                           ('lua', _('Lua')),
                           ('rst', _('Restructured Text')),
                           ('ruby', _('Ruby')),
                           ('xml', _('XML')))

    series = models.ForeignKey('Series')
    question = RichTextField(_('Question'))
    typical_duration = models.IntegerField(_('Typical duration to answer'),
                                           help_text=_('Expressed in seconds.'))
    minimum_duration = models.IntegerField(_('Minimum duration to answer'))
    prefilled_answer = models.TextField(_('Prefilled answer'), blank=True, null=True)
    editor_mode = models.CharField(_('Editor mode'), choices=EDITOR_MODE_CHOICES,
                                   max_length=30, blank=True, null=True)

    def __unicode__(self):
        return u'Question %s' % self.pk

    def open(self, test):
        """ Get an anwser object for this question, binded to the provided test.
        """
        answer = Answer(test=test, question=self)
        answer.save()
        return answer

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')


class Test(models.Model):

    """ A test ... to an applicant.
    """

    id = models.CharField(max_length=4, primary_key=True, default=gen_random_id)
    # state = FSMField(default='created')
    instructions = models.TextField(_('Instructions'), blank=True, null=True)
    series = models.ManyToManyField('Series')
    recruiter = models.ForeignKey('auth.User')
    applicant = models.ForeignKey('Applicant')
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    maximum_duration = models.IntegerField(_('Maximum duration of the test'),
                                           help_text=_('Expressed in minutes.'),
                                           blank=True, null=True)

    # Fields relative to test state (completed when answering):
    cur_answer = models.ForeignKey('Answer', blank=True, null=True, related_name='answered_by')
    cur_series = models.ForeignKey('Series', blank=True, null=True, related_name='answering_by')

    def __unicode__(self):
        return u'Test for %s' % self.applicant

    class Meta:
        verbose_name = _('test')
        verbose_name_plural = _('tests')

    def get_absolute_url(self):
        return reverse('test_index', args=[self.pk])

    @property
    def already_answered_series(self):
        """ Get the set of series already answered by the applicant for this test.
        """
        return set([x.question.series for x in self.answer_set.filter(end_to_answer_date__isnull=False)])

    def can_answer(self):
        """ Return True if the test is still anwerable (= not expired)
        """
        return self.start_date + timedelta(seconds=self.maximum_duration * 60) > datetime.now()

    @property
    def remaining_seconds(self):
        """ Return the remaining duration of the test in seconds.

        Return None if no maximum duration is provided or maximum duration * 60
        if test is not yet started.
        """
        if self.maximum_duration is None:
            return None
        elif self.start_date is None:
            return self.maximum_duration * 60
        else:
            duration = timedelta(seconds=self.maximum_duration * 60)
            remaining = duration - (datetime.now(self.start_date.tzinfo) - self.start_date)
            seconds = remaining.total_seconds()
            if seconds <= 0:
                return 0
            else:
                return seconds

    @property
    def progress(self):
        """ Return a tuple of (answered, total) number of questions.
        """
        answered = self.answer_set.filter(end_to_answer_date__isnull=False).count()
        total = Question.objects.filter(series__in=self.series.all()).count()
        return answered, total

    @property
    def is_finished(self):
        """ Return True if the test is finished, also set the end_date if not
        already set.
        """
        answered, total = self.progress
        if any((answered == total, self.remaining_seconds == 0)):
            # Close the test:
            if self.end_date is None:
                self.end_date = datetime.now()
                self.save()
            # Close the last uncompleted answer (if any):
            answer = self.answer_set.filter(end_to_answer_date__isnull=True)
            if answer:
                answer = answer[0]
                answer.complete(skip=True)
            return True
        else:
            return False

    @property
    def is_started(self):
        """ Return True if the test has started.
        """
        return self.start_date is not None

    def next_question(self):
        """ Open and return the next question of the series.
        """
        if self.start_date is None:
            self.start_date = datetime.now()

        question = self.cur_series.get_first_unanswered(self)
        if question is None:  # When no more question are unanswered in the series
            self.cur_answer = None
            self.cur_series = None
        else:
            self.cur_answer = question.open(self)
        self.save()
        return self.cur_answer


class Answer(models.Model):

    """ An answer to a question by the applicant.
    """

    test = models.ForeignKey('Test')
    question = models.ForeignKey('Question')
    answer = models.TextField(_('Answer'), blank=True, null=True)

    start_to_answer_date = models.DateTimeField(auto_now_add=True)
    end_to_answer_date = models.DateTimeField(blank=True, null=True)

    def complete(self, answer, skip=False):
        """ Complete this anwser.
        """
        self.answer = answer
        self.end_to_answer_date = datetime.now()
        self.save()

    @property
    def duration(self):
        """ Return a timedelta of the duration of the answer.
        """
        if self.end_to_answer_date is None:
            end_to_answer = datetime.now(self.start_to_answer_date.tzinfo)
        else:
            end_to_answer = self.end_to_answer_date
        return end_to_answer - self.start_to_answer_date

    class Meta:
        verbose_name = _('answer')
        verbose_name_plural = _('answers')
        unique_together = ('question', 'test')

    def __unicode__(self):
        return u'Answer for %s' % self.question
