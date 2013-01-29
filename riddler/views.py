from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict

from riddler.models import Test, Series
from riddler.forms import AnswerForm, ShortcodeForm


def home(request):
    """ Riddler index page.
    """
    if request.method == 'POST':
        shortcode_form = ShortcodeForm(request.POST)
        if shortcode_form.is_valid():
            print
            return redirect('test_index', test_id=shortcode_form.cleaned_data['shortcode'])
    else:
        shortcode_form = ShortcodeForm()
    return render(request, 'home.html', {'shortcode_form': shortcode_form})


def test_index(request, test_id):
    """ Index page for a test.
    """
    test = get_object_or_404(Test, pk=test_id)
    if test.is_finished:
        return render(request, 'test_finished.html', {'test': test})

    answered = test.already_answered_series
    series = []
    for a_series in test.series.all():
        if a_series == test.cur_series:
            status = 'answering'
        elif a_series in answered:
            status = 'answered'
        else:
            status = 'to_answer'
        a_series_dict = model_to_dict(a_series)
        a_series_dict.update({'status': status})
        series.append(a_series_dict)
    env = {'series': series, 'test_id': test.pk, 'test': test}
    return render(request, 'test_index.html', env)


def start_to_answer_series(request, test_id, series_id):
    """ Set the current answered series of a test and redirect to the
        answering page.
    """

    test = get_object_or_404(Test, pk=test_id)
    if test.is_finished:
        return redirect('test_index', test_id=test.pk)

    if test.cur_series is not None:
        return redirect('answering_question', test_id=test.pk)

    series = get_object_or_404(Series, pk=series_id)
    if series in test.already_answered_series:
        return redirect('test_index', test_id=test.pk)

    test.cur_series = series
    if test.next_question() is None:  # Handle the case when no question is in series
        return redirect('test_index', test_id=test.pk)

    test.save()

    return redirect('start_to_answer_series', test_id=test.pk, series_id=series.pk)


def answering_question(request, test_id):
    test = get_object_or_404(Test, pk=test_id)

    # Redirect the user to the test index if it's finished:
    if test.is_finished:
        return redirect('test_index', test_id=test.pk)

    # Redirect the user to the test index if no series is currently selected:
    if test.cur_series is None:
        return redirect('test_index', test_id=test.pk)

    question = test.cur_answer.question

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            test.cur_answer.complete(answer_form.cleaned_data['answer'])
            test.cur_answer.save()
            answer = test.next_question()
            if answer is None:  # End of the series
                return redirect('test_index', test_id=test.pk)
            else:
                return redirect('answering_question', test_id=test.pk)
    else:
        answer_form = AnswerForm()

    env = {'question': question, 'answer_form': answer_form, 'test': test}
    return render(request, 'answering_question.html', env)