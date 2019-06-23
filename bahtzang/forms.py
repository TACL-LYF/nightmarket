from django import forms
from . import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class CamperLookupForm(forms.Form):
    first_name = forms.CharField(required = True)
    last_name = forms.CharField(required = True)


class CamperSelectForm(forms.Form):
    register_new_sibling = forms.BooleanField()
    def __init__(self, sibling_sets,  *args, **kwargs):
        super(CamperSelectForm, self).__init__(*args, **kwargs)

        for sibling_set in sibling_sets:
            for sibling in sibling_set['siblings']:
                self.fields['{}'.format(sibling.pk)] = forms.BooleanField()

class NewSiblingForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=50, required=True)
    last_name = forms.CharField(label='Last name', max_length=50, required=True)
    gender = forms.ChoiceField(label='Gender', choices=models.Camper.GENDER_CHOICES, required=True)
    birthdate = forms.DateField(label='Birthdate', widget=forms.SelectDateWidget, required=True)
    grade = forms.IntegerField(label='Grade for next year', validators=[MinValueValidator(3), MaxValueValidator(12)], required=True)

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
    stripeToken = forms.CharField(required=True)

class AlternatePaymentForm(forms.Form):
    payment_type = forms.ChoiceField(choices=models.Registration_Payment.PAYMENT_METHODS, widget=forms.RadioSelect, required=True)
    check_number = forms.IntegerField(required=False)
