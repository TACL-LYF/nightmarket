from django.shortcuts import render
from . import models
from . import forms
from django.shortcuts import redirect

def preregistration_landing(request):
    if request.method == 'POST':
        camper_sibling_list = camper_lookup(request)
        if len(camper_sibling_list) == 0:
            return render(request, 'bahtzang/preregistration_landing.html', {
                'camper_lookup_form': forms.CamperLookupForm(),
                'error': 'Camper lookup failed - check for spelling errors'
        })
        return render(request, 'bahtzang/camper_lookup.html', {
            'camper_sibling_list': camper_sibling_list
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
        campers = models.Camper.objects.filter(first_name__iexact = first_name, last_name__iexact = last_name)
        camper_sibling_list = []
        # also grab siblings for each camper
        for camper in campers:
            family = models.Family.objects.filter(pk = camper.family)
            # In the future, update so that it only grabs campers that haven't graduated yet
            siblings = models.Camper.objects.filter(family = family.id)
            camper_sibling_list.append(siblings)

        return camper_sibling_list
    else:
        return "Error, ask Rosette for assistance"

def create_new_preregistration(request):
    if request.method == 'POST':
        form = forms.CamperLookupForm(request)
    else:
        return "Error, ask Rosette for assistance"

