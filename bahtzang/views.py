from django.shortcuts import render
from . import models
from . import forms
from django.shortcuts import redirect
from django.core import serializers

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
                return render(request, 'bahtzang/lookup.html', {
                    'camper_lookup_form': forms.CamperLookupForm(),
                    'error': 'Camper lookup failed - check for spelling errors'
            })
            return render(request, 'bahtzang/select.html', {
                'sibling_sets': sibling_sets
            })

    return render(request, 'bahtzang/lookup.html', {
        'camper_lookup_form': forms.CamperLookupForm(),
        'error': "Something went wrong - go to Rosette's booth"
        })

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
        request.session['price'] = int(price)

        return render(request, 'bahtzang/update.html', {
            'campers': camper_qs,
            'contact_update_form': form,
            'price': price
            })
    return render(request, 'bahtzang/select.html', {
        'camper_lookup_form': forms.CamperLookupForm()
        })

def payment(request):
    if request.method == 'POST':
        form = forms.ContactUpdateForm(request.POST)
        if form.is_valid():
            print('Passed validation, update model here')
            family = form.save(commit=False)
            request.session['family'] = serializers.serialize("json", [family])
            campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        return render(request, 'bahtzang/payment.html', {
            'campers': campers,
            })

def confirm(request):
    if request.method == 'POST':
        campers = [ds_obj.object for ds_obj in serializers.deserialize("json", request.session['campers'])]
        family = list(serializers.deserialize("json", request.session['family']))[0].object
        return render(request, 'bahtzang/confirmation.html', {
            'campers': campers,
            'family': family
            })