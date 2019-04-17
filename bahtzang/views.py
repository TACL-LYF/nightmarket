from django.shortcuts import render, redirect
from django.urls import reverse
from . import models
from . import forms
from django.shortcuts import redirect
from django.core import serializers
from django.contrib import messages

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
                # TODO: only grab campers that haven't graduated yet
                siblings = models.Camper.objects.filter(family = camper.family.id)
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
        request.session['price'] = int(price)

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
        price = request.session['price']
        form = forms.ContactUpdateForm(request.POST, instance=family)

        if form.is_valid():
            print('Passed validation, update model here')
            family = form.save()
            request.session['family'] = serializers.serialize("json", [family])
            return render(request, 'bahtzang/payment.html', {
                'campers': campers,
                })
        else:
            messages.error(request, "Invalid form - could not update contact information")
            if len(form.errors) > 0:
                for field in form.errors:
                    error_msg = ', '.join(form.errors[field])
                    messages.error(request, '{}: {}'.format(field, error_msg))
            return render(request, 'bahtzang/update.html', {
                'campers': campers,
                'contact_update_form': form,
                'price': price
                })
    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))

def confirm(request):
    if request.method == 'POST':
        campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        family = list(serializers.deserialize("json", request.session['family']))[0].object
        for camper in campers:
            # camper.preregister()
            pass
        return render(request, 'bahtzang/confirmation.html', {
            'campers': campers,
            'family': family
            })

    messages.error(request, "Did not receive POST request - are you using your browser's back button?")
    return redirect(reverse('bahtzang:lookup'))