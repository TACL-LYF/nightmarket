from django.shortcuts import render, get_object_or_404
from . import models
from . import forms
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView


TEMPLATES = {"lookup": "bahtzang/lookup.html",
             "select": "bahtzang/select.html",
             "update": "bahtzang/update.html"}
             # "checkout": "bahtzang/checkout.html",
             # "confirm": "bahtzang/confirm.html"}

class PreregisterWizard(SessionWizardView):
    form_list = [forms.CamperLookupForm, 
                 forms.CamperSelectForm, 
                 forms.ParentUpdateForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(PreregisterWizard, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == 'select':
            data = self.get_cleaned_data_for_step('lookup')
            form = forms.CamperSelectForm(data)
        elif step == 'update':
            camper_ids = [cid for cid in self.request.POST.keys() if cid not in ['csrfmiddlewaretoken', 'preregister_wizard-current_step']]
            if len(camper_ids) > 0:
                campers = models.Camper.objects.filter(pk__in = camper_ids)
                instance = campers[0].family
                form = forms.ParentUpdateForm(instance=instance)
                form.campers = campers

        return form

    def get_context_data(self, form, **kwargs):
        context = super(PreregisterWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'select':
            context.update({'families': form.families})
        if self.steps.current == 'update':
            context.update({'campers': form.campers})
        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        for form in form_list: 
            print(form.cleaned_data)
        return render(self.request, 'bahtzang/confirmation.html', {
            'form_data': [form.cleaned_data for form in form_list]
        })


