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

# def register_new_sibling(request):
    # if request.method == 'GET':


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

def update_add_new_sibling(request):
    family = list(serializers.deserialize("json", request.session['family']))[0].object
    campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
    price = Decimal(json.loads(request.session['price']))
    try:
        new_camper_grades = json.loads(request.session['new_camper_grades'])
    except KeyError:
        new_camper_grades = []

    if request.method == 'GET':
        form = forms.NewSiblingForm()
        return render(request, 'bahtzang/new_sibling.html', {
            'campers': campers,
            'new_sibling_form': form,
            'price': price
            })
    elif request.method == 'POST':
        form = forms.NewSiblingForm(request.POST)
        if form.is_valid():
            # create new camper
            new_camper = models.Camper(first_name=form.cleaned_data['first_name'],
                                       last_name=form.cleaned_data['last_name'],
                                       gender=int(form.cleaned_data['gender']),
                                       birthdate=form.cleaned_data['birthdate'],
                                       family=family,
                                       returning=False)
            new_camper_grades.append(form.cleaned_data['grade'])
            
            # update campers and price
            campers.append(new_camper)
            price = price + models.Camp.objects.filter(year = '2019').get().registration_fee
            
            # reserialize everything
            request.session['campers'] = serializers.serialize("json", campers)
            request.session['new_camper_grades'] = json.dumps(new_camper_grades)
            request.session['price'] = json.dumps(Decimal(price), cls=DjangoJSONEncoder)

            form = forms.ContactUpdateForm(instance=family)

            return render(request, 'bahtzang/update.html', {
                'campers': campers,
                'contact_update_form': form,
                'price': price
                })
 
        else:
            messages.error(request, "Something went wrong with adding a new camper.")
            return render(request, 'bahtzang/update.html', {
                'campers': campers,
                'contact_update_form': form,
                'price': price
                })


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

def alternate_payment(request):
    campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
    family = list(serializers.deserialize("json", request.session['family']))[0].object
    price = Decimal(json.loads(request.session['price']))
    donation_amount = Decimal(json.loads(request.session['donation']))

    return render(request, 'bahtzang/alternate.html', {
        'campers': campers,
        'price': price,
        'donation': donation_amount,
        'total': price + donation_amount,
        'form': forms.AlternatePaymentForm()
    })

def confirm(request):
    if request.method == 'POST':
        campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        family = list(serializers.deserialize("json", request.session['family']))[0].object
        price = Decimal(json.loads(request.session['price']))
        new_camper_grades = json.loads(request.session['new_camper_grades'])
        donation_amount = Decimal(json.loads(request.session['donation']))
        payment_amount = price + donation_amount
        stripe_form = forms.StripeTokenForm(request.POST)
        alternate_form = forms.AlternatePaymentForm(request.POST)

        context = {
            'campers': campers,
            'price': price,
            'donation': donation_amount,
            'total': price + donation_amount
        }

        preregistrations = []
        # create and validate registrations
        for camper in campers:
            try:
                if camper.returning:
                    preregistrations.append(camper.create_and_validate_preregistration())
                else:
                    preregistrations.append(camper.create_and_validate_preregistration(new_camper=True, grade=new_camper_grades.pop(0)))
            except (errors.InactiveCamper, errors.RegistrationAlreadyExists) as e:
                messages.error(request, e)
                return render(request, 'bahtzang/payment.html', context)
            except IndexError:
                messages.error(request, 'Something went wrong - likely with preregistering new siblings')
                return render(request, 'bahtzang/payment.html', context)

        if stripe_form.is_valid():
            try:
                # charge card
                token = stripe_form.cleaned_data['stripeToken']
                charge_desc = 'Preregistration for 2020 - {}'.format(', '.join(['{} {}'.format(camper.first_name, camper.last_name) for camper in campers]))
                charge = stripe.Charge.create(
                    amount=int(payment_amount * 100),
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
                total=payment_amount,
                stripe_charge_id=charge['id'],
                stripe_brand=charge["payment_method_details"]['card']['brand'],
                stripe_last_four=charge["payment_method_details"]['card']['last4']
                )


        elif alternate_form.is_valid():
            # create registration payment
            payment_method = int(alternate_form.cleaned_data['payment_type'])
            if payment_method == 1: # check
                payment = models.Registration_Payment(
                    payment_method=payment_method, additional_donation=donation_amount, 
                    total=payment_amount, check_number=int(alternate_form.cleaned_data['check_number']))
            elif payment_method == 2: # cash
                payment = models.Registration_Payment(
                    payment_method=payment_method, additional_donation=donation_amount, 
                    total=payment_amount)
            else:
                messages.error(request, "Invalid or missing choice for payment method provided")
                return render(request, 'bahtzang/payment.html', context)

        else:
            messages.error(request, "Could not validate Stripe token. Double check payment information.")
            return render(request, 'bahtzang/payment.html', context)

        payment.save()

        # link payment to all registrations
        for camper, preregistration in zip(campers, preregistrations):
            preregistration.registration_payment = payment
            if not camper.returning:
                camper.save()
            preregistration.save()

        return render(request, 'bahtzang/confirmation.html', {
            'campers': campers,
            'family': family
            })
    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))

