from django.shortcuts import render, redirect
from django.urls import reverse
from . import models
from . import forms
from . import errors
from django.shortcuts import redirect
from django.core import serializers
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from decimal import Decimal
from django.conf import settings
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

def lookup(request):
    return render(request, 'bahtzang/lookup.html', {
        'camper_lookup_form': forms.CamperLookupForm()
        })

def select(request):
    if request.method == 'POST':
        form = forms.CamperLookupForm(request.POST)
        if form.is_valid():
            first_name, last_name = form.cleaned_data['first_name'], form.cleaned_data['last_name']
            camper_qs = models.Camper.objects.filter(first_name__iexact = first_name, last_name__iexact = last_name)
            sibling_sets = []
            # also grab siblings for each camper
            for camper in camper_qs:
                siblings = []
                for sibling in models.Camper.objects.filter(family = camper.family.id):
                    if len(models.Registration.objects.filter(camper_id = sibling.id, camp__year = '2019')) > 0:
                        sibling.registered = True
                    else:
                        sibling.registered = False
                    siblings.append(sibling)
                family = models.Family.objects.filter(pk = camper.family.id).get()
                sibling_sets.append({'family': family, 'siblings': siblings})

            if len(sibling_sets) == 0:
                messages.error(request, 'Camper lookup failed - check for spelling errors')
                return redirect(reverse('bahtzang:lookup'))

            return render(request, 'bahtzang/select.html', {
                'sibling_sets': sibling_sets
            })

    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))

def update(request):
    if request.method == 'POST':
        camper_pks = []
        for camper_pk, checked in request.POST.dict().items():
            if camper_pk == 'csrfmiddlewaretoken' or checked != 'on':
                continue
            camper_pks.append(camper_pk)

        camper_qs = models.Camper.objects.filter(pk__in = camper_pks)
        price = len(camper_qs) * models.Camp.objects.filter(year = '2019').get().registration_fee
        form = forms.ContactUpdateForm(instance=camper_qs[0].family)

        request.session['campers'] = serializers.serialize("json", camper_qs)
        request.session['family'] = serializers.serialize("json", [camper_qs[0].family])
        request.session['price'] = json.dumps(Decimal(price), cls=DjangoJSONEncoder)

        return render(request, 'bahtzang/update.html', {
            'campers': camper_qs,
            'contact_update_form': form,
            'price': price
            })

    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))

def donation(request):
    if request.method == 'POST':
        family = list(serializers.deserialize("json", request.session['family']))[0].object
        campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        price = Decimal(json.loads(request.session['price']))
        form = forms.ContactUpdateForm(request.POST, instance=family)

        if form.is_valid():
            print('Passed validation, update model here')
            family = form.save()
            request.session['family'] = serializers.serialize("json", [family])
            return render(request, 'bahtzang/donation.html', {
                'donation_form': forms.DonationForm()
                })
        else:
            messages.error(request, "Invalid form - could not update contact information")
            if len(form.errors) > 0:
                for field in form.errors:
                    error_msg = ', '.join(form.errors[field])
                    messages.error(request, '{}: {}'.format(field, error_msg))
            return render(request, 'bahtzang/update.html', {
                'campers': camper_qs,
                'contact_update_form': form,
                'price': price
                })

    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))

def payment(request):
    if request.method == 'POST':
        family = list(serializers.deserialize("json", request.session['family']))[0].object
        campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        price = Decimal(json.loads(request.session['price']))
        form = forms.DonationForm(request.POST)
        if form.is_valid():
            donation_amount = round(form.cleaned_data['donation_amount'], 2)
            request.session['total'] = json.dumps(price + donation_amount, cls=DjangoJSONEncoder)
            request.session['donation'] = json.dumps(donation_amount, cls=DjangoJSONEncoder)
            return render(request, 'bahtzang/payment.html', {
                'campers': campers,
                'price': price,
                'donation': donation_amount,
                'total': price + donation_amount,
                'stripe_pk': settings.STRIPE_PUBLIC_KEY,
                })
        else:
            messages.error(request, "Invalid donation amount")
            if len(form.errors) > 0:
                for field in form.errors:
                    error_msg = ', '.join(form.errors[field])
                    messages.error(request, '{}: {}'.format(field, error_msg))
            return render(request, 'bahtzang/donation.html', {
                'donation_form': forms.DonationForm()
                })
    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))



def confirm(request):
    if request.method == 'POST':
        campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        family = list(serializers.deserialize("json", request.session['family']))[0].object
        price = Decimal(json.loads(request.session['price']))
        donation_amount = Decimal(json.loads(request.session['donation']))
        form = forms.StripeTokenForm(request.POST)
        context = {
            'campers': campers,
            'price': price,
            'donation': donation_amount,
            'total': price + donation_amount,
            'stripe_token_form': forms.StripeTokenForm()
        }
        if form.is_valid():

            preregistrations = []
            # create and validate registrations
            for camper in campers:
                try:
                    preregistrations.append(camper.create_and_validate_preregistration())
                except (errors.InactiveCamper, errors.RegistrationAlreadyExists) as e:
                    messages.error(request, e)
                    return render(request, 'bahtzang/payment.html', context)
                preregistrations.append(camper.preregister())

            # charge card
            token = form.cleaned_data['stripeToken']
            charge_amount = price + donation_amount
            charge_desc = 'Preregistration for 2020 - {}'.format(', '.join(['{} {}'.format(camper.first_name, camper.last_name) for camper in campers]))
            
            try:
                charge = stripe.Charge.create(
                    amount=int(charge_amount * 100),
                    currency='usd',
                    source=token,
                    description=charge_desc)
            except stripe.error.CardError as e:
                messages.error(request, "Card error: {}".format(e))
                return render(request, 'bahtzang/payment.html', context)

            # create registration payment
            payment = models.Registration_Payment(
                payment_method=0,
                additional_donation=donation_amount,
                total=charge['amount'] / 100,
                stripe_charge_id=charge['id'],
                stripe_brand=charge["payment_method_details"]['card']['brand'],
                stripe_last_four=charge["payment_method_details"]['card']['last4']
                )

            payment.save()

            # link payment to all registrations
            for preregistration in preregistrations:
                preregistration.registration_payment = payment
                preregistration.save()


            return render(request, 'bahtzang/confirmation.html', {
                'campers': campers,
                'family': family
                })
        else:
            messages.error(request, "Could not validate Stripe token. Double check payment information.")
            return render(request, 'bahtzang/payment.html', context)

    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))

