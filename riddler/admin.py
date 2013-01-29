from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from imperavi.admin import ImperaviAdmin, ImperaviStackedInlineAdmin
from imperavi.widget import ImperaviWidget

from riddler.models import RichTextField, Applicant, Test, Series, Question


# Override the Imperavi admin classes to reassociate its widget to our
# RichTextField models field:

class ImperaviAdmin(ImperaviAdmin):

    formfield_overrides = {RichTextField: {'widget': ImperaviWidget}}


class ImperaviStackedInlineAdmin(ImperaviStackedInlineAdmin):

    formfield_overrides = {RichTextField: {'widget': ImperaviWidget}}


class ApplicantAdmin(ImperaviAdmin):

    list_display = ('fullname', 'tests_count', 'last_test')

    def tests_count(self, applicant):
        return applicant.test_set.count()

    def last_test(self, applicant):
        tests = applicant.test_set.order_by('-creation_date')
        if tests:
            return tests[0].creation_date
        else:
            return _('None')


admin.site.register(Applicant, ApplicantAdmin)


class TestAdmin(ImperaviAdmin):

    unique_media = True
    list_display = ('applicant', 'creation_date', 'progress', 'recruiter', 'link')
    fieldsets = ((None, {'fields': ('instructions', 'series', 'applicant',
                                    'recruiter', 'maximum_duration')}),
                 ('Internal', {'classes': ('collapse',),
                               'description': '/!\\ do not touch unless you know what you are doing /!\\',
                               'fields': ('cur_series', 'cur_answer')}))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Set the recruiter default value as current logged user:
        if db_field.name == 'recruiter':
            kwargs['initial'] = request.user.id
        return super(TestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def state(self, test):
        if test.start_date is None and test.end_date is None:
            return _('Ready to start')
        elif test.start_date is not None and test.end_date is None:
            return _('In progress')
        else:
            return _('Ended')

    def link(self, test):
        """ Return a link to the test.
        """
        link = u'<a href="%s">%s %s</a>' % (test.get_absolute_url(), _('Test'), test.pk)
        report = u'<a href="%s">%s</a>' % (reverse('admin:test_report', args=[test.pk]), _('Report'))
        return link + u' | ' + report
    link.allow_tags = True

    def progress(self, test):
        """ Return a progress bar for the test.
        """
        answered, total = test.progress
        env = {'percentage': float(answered) / total * 100,
               'state': self.state(test)}
        return (u'<div class="progressbar"><div class="progress" style="width: '
                 '%(percentage)d%%"></div><div class="text">'
                 '<strong>%(state)s</strong> (%(percentage)d %%)</div></div>' % env)
    progress.allow_tags = True

    def get_urls(self):
        urls = super(TestAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<test_id>.{4})/report/$', self.admin_site.admin_view(self.report_view), name='test_report')
        )
        return my_urls + urls

    def report_view(self, request, test_id):
        """ Generate the report view in the admin.
        """
        test = get_object_or_404(Test, pk=test_id)

        answers = test.answer_set.order_by('start_to_answer_date')
        answer_by_series = []
        for answer in answers:
            if not answer_by_series or answer_by_series[-1]['series'] != answer.question.series:
                answer_by_series.append({'series': answer.question.series,
                                         'duration': 0,
                                         'answers': []})
            series = answer_by_series[-1]
            series['duration'] += answer.duration.total_seconds()
            series['answers'].append(answer)

        env = {'opts': self.model._meta, 'app_label': self.model._meta.app_label,
               'original': test, 'has_change_permission': self.has_change_permission(request, test),
               'answer_by_series': answer_by_series}
        return render(request, 'admin_report.html', env, current_app=self.admin_site.name)


admin.site.register(Test, TestAdmin)


class InlineQuestion(ImperaviStackedInlineAdmin):
    model = Question


class SeriesAdmin(ImperaviAdmin):

    list_display = ('name', 'questions', 'estimated_duration')
    fields = ('name', 'instructions')
    inlines = (InlineQuestion, )

    def estimated_duration(self, series):
        return _('%d min.') % series.duration


admin.site.register(Series, SeriesAdmin)