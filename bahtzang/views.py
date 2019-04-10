from django.shortcuts import render
from . import models
from . import forms
from django.shortcuts import redirect

def preregistration_landing(request):
    if request.method == 'POST':
        sibling_sets = camper_lookup(request)
        if len(sibling_sets) == 0:
            return render(request, 'bahtzang/preregistration_landing.html', {
                'camper_lookup_form': forms.CamperLookupForm(),
                'error': 'Camper lookup failed - check for spelling errors'
        })
        return render(request, 'bahtzang/camper_lookup.html', {
            'sibling_sets': sibling_sets
        })
    elif request.method == 'GET':
        return render(request, 'bahtzang/preregistration_landing.html', {
            'camper_lookup_form': forms.CamperLookupForm()
        })
    else:
        return "Error, ask Rosette for assistance"

def camper_lookup(request):
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
        return sibling_sets
    else:
        return "Error, ask Rosette for assistance"

def create_new_preregistration(request):
    if request.method == 'POST':
        form = forms.CamperLookupForm(request)
    else:
        return "Error, ask Rosette for assistance"

def checkout(request):
    if request.method == 'POST':
        camper_pks = []
        for camper_pk, checked in request.POST.dict().items():
            if camper_pk == 'csrfmiddlewaretoken' or checked != 'on':
                continue
            camper_pks.append(camper_pk)

        camper_qs = models.Camper.objects.filter(pk__in = camper_pk)
        # price = len(camper_qs) * models.Camp.objects.filter(year = '2019').get().registration_fee


    elif request.method == 'GET':
        return render(request, 'bahtzang/preregistration_landing.html', {
            'camper_lookup_form': forms.CamperLookupForm()
        })
