from django.shortcuts import render
from . import models
from . import forms
from django.shortcuts import redirect

def preregistration_landing(request):
    return render(request, 'bahtzang/preregistration_landing.html', {
        'camper_lookup_form': forms.CamperLookupForm()
    })

def camper_lookup(request):
    if request.method == 'POST':
        form = forms.CamperLookupForm(request.POST)
        campers = models.Camper.objects.filter(first_name = form.first_name, last_name = form.last_name)

        camper_sibling_list = []
        # also grab siblings for each camper
        for camper in campers:
            family = models.Family.objects.filter(pk = camper.family)
            # In the future, update so that it only grabs campers that haven't graduated yet
            siblings = models.Camper.objects.filter(family = family.id)
            camper_sibling_list.append(siblings)

        return render(request, 'bahtzang/camper_lookup.html', {
            'camper_sibling_list': camper_sibling_list
        })
    else:
        redirect(preregistration_landing)




def create_new_preregistration(request):
    if request.method == 'POST':
        form = forms.CamperLookupForm(request)
    else:
        return "Error, ask Rosette for assistance"

