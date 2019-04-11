from django.shortcuts import render
from . import models
from . import forms
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView


TEMPLATES = {"lookup": "bahtzang/preregistration_landing.html",
             "select": "bahtzang/camper_lookup.html"}


# def preregistration_landing(request):
#     if request.method == 'POST':
#         sibling_sets = camper_lookup(request)
#         if len(sibling_sets) == 0:
#             return render(request, 'bahtzang/preregistration_landing.html', {
#                 'camper_lookup_form': forms.CamperLookupForm(),
#                 'error': 'Camper lookup failed - check for spelling errors'
#         })
#         return render(request, 'bahtzang/camper_lookup.html', {
#             'sibling_sets': sibling_sets
#         })
#     elif request.method == 'GET':
#         return render(request, 'bahtzang/preregistration_landing.html', {
#             'camper_lookup_form': forms.CamperLookupForm()
#         })
#     else:
#         return "Error, ask Rosette for assistance"

# def camper_lookup(request):
#     import pdb
#     pdb.set_trace()
#     form = forms.CamperLookupForm(request.POST)
#     if form.is_valid():
#         first_name, last_name = form.cleaned_data['first_name'], form.cleaned_data['last_name']
#         camper_qs = models.Camper.objects.filter(first_name__iexact = first_name, last_name__iexact = last_name)
#         sibling_sets = []
#         # also grab siblings for each camper
#         for camper in camper_qs:
#             # TODO: only grab campers that haven't graduated yet
#             siblings = models.Camper.objects.filter(family = camper.family.id)
#             family = models.Family.objects.filter(pk = camper.family.id).get()
#             sibling_sets.append({'family': family, 'siblings': siblings})
#         return sibling_sets
#     else:
#         return "Error, ask Rosette for assistance"

# def create_new_preregistration(request):
#     if request.method == 'POST':
#         form = forms.CamperLookupForm(request)
#     else:
#         return "Error, ask Rosette for assistance"

# def checkout(request):
#     if request.method == 'POST':
#         camper_pks = []
#         for camper_pk, checked in request.POST.dict().items():
#             if camper_pk == 'csrfmiddlewaretoken' or checked != 'on':
#                 continue
#             camper_pks.append(camper_pk)

#         camper_qs = models.Camper.objects.filter(pk__in = camper_pk)
#         # price = len(camper_qs) * models.Camp.objects.filter(year = '2019').get().registration_fee


#     elif request.method == 'GET':
#         return render(request, 'bahtzang/preregistration_landing.html', {
#             'camper_lookup_form': forms.CamperLookupForm()
#         })


class PreregisterWizard(SessionWizardView):
    form_list = [forms.CamperLookupForm, forms.CamperSelectForm]

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step == 'select':
            # Update wizard internal state
            data = self.get_cleaned_data_for_step('lookup')
            form_class = self.form_list[step]
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, form_class),
                'initial': self.get_form_initial(step),
            })
            form = forms.CamperSelectForm(data)
        else:
            form = super(PreregisterWizard, self).get_form(step, data, files)
        return form

    def get_context_data(self, form, **kwargs):
        context = super(PreregisterWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'select':
            context.update({'families': form.families})
        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        for form in form_list: 
            print(form.cleaned_data)
        return render(self.request, 'bahtzang/confirmation.html', {
            'form_data': [form.cleaned_data for form in form_list]
        })


