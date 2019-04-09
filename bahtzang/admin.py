from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import *

class ReferralInline(admin.TabularInline):
    model = Referral
    extra = 0
    exclude = ('created_at', 'updated_at',)
    readonly_fields = ['referral_method', 'details']
    show_change_link = True

class CamperInline(admin.TabularInline):
    model = Camper
    extra = 0
    fields = ['first_name', 'last_name', 'gender', 'birthdate', 'status', 'get_registration_links_list']
    readonly_fields = ['get_registration_links_list']
    show_change_link = True

class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    fields = ['camp', 'grade', 'shirt_size', 'bus', 'preregistration',]
    show_change_link = True

class CampAdmin(admin.ModelAdmin):
    def registration_count(self, obj):
        return obj.registration_set.count()
    registration_count.short_description = "Registrations"

    search_fields = ('name',)

    list_display = ('year', 'name', 'registration_count')
    list_display_links = ('year', 'name')
    ordering = ('-year',)

    fieldsets = [
        (None, {'fields': [
            'year', 'name', 'campsite', 'campsite_address', 'camp_start_date',
            'camp_end_date',
        ]}),
        ('Registration Details', {'fields': [
            'registration_open_date', 'registration_late_date',
            'registration_close_date', 'registration_fee', 'registration_late_fee',
            'shirt_price', 'sibling_discount', 'waitlist_starts_after',
        ]})
    ]

class FamilyAdmin(admin.ModelAdmin):
    def campers(self, obj):
        return format_html_join(
            ', ', '<a href="{}">{}</a>',
            ((reverse('admin:bahtzang_camper_change', args=(c.id,)), str(c)) for c in obj.camper_set.all())
        )

    search_fields = ('primary_parent_first_name', 'primary_parent_last_name',
        'primary_parent_email', 'primary_parent_phone_number', 'city',
        'secondary_parent_first_name', 'secondary_parent_last_name',
        'secondary_parent_email', 'secondary_parent_phone_number', 'street')

    list_display = ('primary_parent_first_name', 'primary_parent_last_name',
        'primary_parent_email', 'primary_parent_phone_number', 'city', 'campers')
    list_display_links = ('primary_parent_first_name', 'primary_parent_last_name')

    fieldsets = [
        ('Primary Parent Information', {'fields': [
            ('primary_parent_first_name', 'primary_parent_last_name',),
            ('primary_parent_email', 'primary_parent_phone_number',),
        ]}),
        ('Secondary Parent Information', {'fields': [
            ('secondary_parent_first_name', 'secondary_parent_last_name',),
            ('secondary_parent_email', 'secondary_parent_phone_number',),
        ]}),
        ('Address Information', {'fields': [
            ('street', 'suite',),
            ('city', 'state', 'zip'),
        ]}),
    ]
    inlines = [ReferralInline, CamperInline]

class CamperAdmin(admin.ModelAdmin):
    def link_to_family(self, obj):
        f = obj.family
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:bahtzang_family_change', args=(f.id,)),
            str(f)
        )

    search_fields = ('first_name', 'last_name',
        'medical_conditions_and_medication', 'diet_and_food_allergies')

    list_display = ('first_name', 'last_name', 'gender', 'birthdate', 'email',
        'link_to_family', 'get_registration_links_list', 'status')
    list_display_links = ('first_name', 'last_name')
    list_filter = ('status', 'gender', 'returning', 'registration__camp__year')

    fields = [('status', 'returning',), 'first_name', 'last_name', 'birthdate',
        'gender', 'email', 'medical_conditions_and_medication',
        'diet_and_food_allergies']
    inlines = [RegistrationInline]

class RegistrationAdmin(admin.ModelAdmin):
    def link_to_camper(self, obj):
        c = obj.camper
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:bahtzang_camper_change', args=(c.id,)),
            str(c)
        )
    link_to_camper.short_description = 'Camper'
    link_to_camper.admin_order_field = 'camper'

    def link_to_family(self, obj):
        f = obj.camper.family
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:bahtzang_camper_change', args=(f.id,)),
            str(f)
        )
    link_to_family.short_description = 'Parent'
    link_to_family.admin_order_field = 'family'

    def get_gender(self, obj):
        return obj.camper.gender
    get_gender.short_description = 'Gender'

    def get_medical(self, obj):
        return obj.camper.medical_conditions_and_medication
    get_medical.short_description = 'Medical'

    def get_allergies(self, obj):
        return obj.camper.diet_and_food_allergies
    get_allergies.short_description = 'Diet/Allergies'

    search_fields = ('camper__first_name', 'camper__last_name')

    list_display = ('created_at', 'link_to_camper', 'link_to_family',
        'grade', 'get_gender', 'shirt_size', 'additional_shirts', 'bus',
        'jtasa_chapter', 'camper_involvement', 'get_medical', 'get_allergies', 'additional_notes',
        'status')
    list_filter = ('camp__year', 'status', 'preregistration')

    fields = [('status', 'preregistration'), ('camper', 'camp'), ('grade', 'bus'),
        'shirt_size', 'additional_shirts', 'jtasa_chapter', 'camper_involvement',
        'additional_notes', 'registration_payment', ('created_at', 'updated_at'),
        ('group','camp_family', 'cabin')
    ]
    readonly_fields = 'registration_payment', 'created_at', 'updated_at'

class RegistrationPaymentRegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = fields = ['camp', 'camper', 'additional_shirts']
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

class RegistrationPaymentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('created_at', 'get_registration_links_list', 'discount_code',
        'additional_donation', 'total', 'stripe_brand', 'get_stripe_link')

    inlines = [RegistrationPaymentRegistrationInline]

    readonly_fields = fields = ('discount_code', 'additional_donation', 'total',
        'stripe_brand', 'stripe_last_four', 'get_stripe_link', 'breakdown',
        'created_at', 'updated_at', )

class RegistrationDiscountAdmin(admin.ModelAdmin):
    def link_to_registration_payment(self, obj):
        rp = obj.registration_payment
        if rp == None:
            return rp
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:bahtzang_registration_payment_change', args=(rp.id,)),
            str(rp)
        )
    link_to_registration_payment.short_description = 'Registration Payment'

    list_display = ('code', 'camp', 'discount_percent', 'redeemed',
        'link_to_registration_payment')
    list_filter = ('camp', 'redeemed')

    readonly_fields = ('redeemed', 'registration_payment', 'created_at',
        'updated_at')

class ReferralMethodAdmin(admin.ModelAdmin):
    def referral_count(self, obj):
        return obj.referral_set.count()
    referral_count.short_description = "Referrals"

    list_display = ('name', 'allow_details', 'referral_count')
    list_filter = ('allow_details',)

    fields = (('name', 'allow_details'), 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

class ReferralAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def link_to_family(self, obj):
        f = obj.family
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:bahtzang_camper_change', args=(f.id,)),
            str(f)
        )
    link_to_family.short_description = 'Family'
    link_to_family.admin_order_field = 'family'

    search_fields = ('details',)
    list_display = ('link_to_family', 'referral_method', 'details', 'created_at')
    list_filter = ('referral_method',)
    list_display_links = None

class DonationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

    search_fields = ('first_name', 'last_name', 'company')
    list_display = ('created_at', 'first_name', 'last_name', 'email', 'phone',
        'amount', 'company_match', 'company', 'get_stripe_link')
    readonly_fields = ('first_name', 'last_name', 'email', 'phone', 'address',
        'city', 'state', 'zip', 'amount', 'company_match', 'company',
        'get_stripe_link', 'stripe_brand', 'stripe_last_four', 'created_at',
        'updated_at')

class LastDayPurchaseAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

    search_fields = ('first_name', 'last_name', 'camper_names')
    list_display = ('first_name', 'last_name', 'email', 'phone', 'amount',
        'camper_names', 'get_stripe_link')
    fields = readonly_fields = ('first_name', 'last_name', 'camper_names', 'email',
        'phone', 'address', 'city', 'state', 'zip', 'amount', 'dollar_for_dollar',
        'company', 'get_stripe_link', 'stripe_brand', 'stripe_last_four',)


admin.site.register(Camp, CampAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Camper, CamperAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Registration_Payment, RegistrationPaymentAdmin)
admin.site.register(Registration_Discount, RegistrationDiscountAdmin)
admin.site.register(Referral_Method, ReferralMethodAdmin)
admin.site.register(Referral, ReferralAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(Last_Day_Purchase, LastDayPurchaseAdmin)
