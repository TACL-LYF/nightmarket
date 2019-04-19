from django import forms
from . import models
from decimal import Decimal

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

class DonationForm(forms.Form):
    donation_amount = forms.DecimalField(min_value=0, max_digits=10, initial=0, required=True, decimal_places=2)

class StripeTokenForm(forms.Form):
    stripeToken = forms.CharField()