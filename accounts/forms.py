from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from .models import COUNTRY_CHOICES, UserProfile


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))


class CustomUserCreationForm(UserCreationForm):
    nationality = forms.ChoiceField(
        choices=[('', '-- Select your country --')] + list(COUNTRY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})


class ProfileForm(forms.ModelForm):
    nationality = forms.ChoiceField(
        choices=[('', '-- Select your country --')] + list(COUNTRY_CHOICES),
        required=False,
        label='Nationality',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = UserProfile
        fields = ('nationality',)

    def clean_nationality(self):
        return self.cleaned_data.get('nationality') or None

