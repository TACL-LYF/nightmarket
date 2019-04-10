from django import forms

class CamperLookupForm(forms.Form):
    first_name = forms.CharField(required = True)
    last_name = forms.CharField(required = True)


class CamperSelectForm(forms.Form):
    def __init__(self, sibling_sets,  *args, **kwargs):
        super(CamperSelectForm, self).__init__(*args, **kwargs)
        
        for sibling_set in sibling_sets:
            for sibling in sibling_set['siblings']:
                self.fields['{}'.format(sibling.pk)] = forms.BooleanField()
