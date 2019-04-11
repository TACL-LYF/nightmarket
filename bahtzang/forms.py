from django import forms
from . import models

class CamperLookupForm(forms.Form):
    first_name = forms.CharField(required = True)
    last_name = forms.CharField(required = True)


class CamperSelectForm(forms.Form):
    def __init__(self, data,  *args, **kwargs):
        super(CamperSelectForm, self).__init__(*args, **kwargs)
        
        # Look up campers matching first / last name
        camper_qs = models.Camper.objects.filter(first_name__iexact = data['first_name'], 
            last_name__iexact = data['last_name'])
        
        # Look up siblings for each camper
        families = []
        for camper in camper_qs:
            # TODO: only grab campers that haven't graduated yet
            siblings = models.Camper.objects.filter(family = camper.family.id)
            family = models.Family.objects.filter(pk = camper.family.id).get()
            families.append({'family': family, 'siblings': siblings})
            for sibling in siblings:
                self.fields['{}'.format(sibling.pk)] = forms.BooleanField()

        self.families = families