from django import forms
from . import models

class CamperLookupForm(forms.Form):
    first_name = forms.CharField(required = True)
    last_name = forms.CharField(required = True)


class CamperSelectForm(forms.Form):
    def __init__(self, sibling_sets,  *args, **kwargs):
        super(CamperSelectForm, self).__init__(*args, **kwargs)
        
        for sibling_set in sibling_sets:
            for sibling in sibling_set['siblings']:
                self.fields['{}'.format(sibling.pk)] = forms.BooleanField()

class ContactUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Family
        fields = ['primary_parent_first_name', 'primary_parent_last_name', 
            'primary_parent_email', 'primary_parent_phone_number', 
            'secondary_parent_first_name', 'secondary_parent_last_name', 
            'secondary_parent_email', 'secondary_parent_phone_number']
