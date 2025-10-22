from django import forms
from django.contrib.auth.models import Group
from users.models import User 

class GroupUserForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('nome'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Usuários pertencentes a este grupo"
    )

    class Meta:
        model = Group
        fields = ['name', 'users']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].disabled = True 
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save(self, commit=True):
        group = super().save(commit=False)
        if commit:
            group.save()
        if group.pk:
            group.user_set.set(self.cleaned_data['users'])
        return group
