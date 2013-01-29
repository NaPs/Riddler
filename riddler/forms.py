from django import forms


class AnswerForm(forms.Form):

    """ Answer to a question form.
    """

    answer = forms.CharField(widget=forms.Textarea)


class ShortcodeForm(forms.Form):

    """ Enter a shortcode form.
    """

    shortcode = forms.CharField()