from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext as _
from bahtzang.errors import *
from phonenumber_field.modelfields import PhoneNumberField

class Camp(models.Model):
    year = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    campsite = models.CharField(max_length=100, blank=True)
    campsite_address = models.CharField(max_length=100, blank=True)
    camp_start_date = models.DateField(blank=True)
    camp_end_date = models.DateField(blank=True)
    registration_open_date = models.DateField(blank=True)
    registration_late_date = models.DateField(blank=True)
    registration_close_date = models.DateField(blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    shirt_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    sibling_discount = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    registration_late_fee = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    waitlist_starts_after = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s: %s' % (self.year, self.name)

    def __str__(self):
        return self.full_name

    class Meta:
        managed=False
        ordering = ['year']

        def __unicode__(self):
            return self.title


class Family(models.Model):
    primary_parent_first_name = models.CharField('First Name', max_length=50)
    primary_parent_last_name = models.CharField('Last Name', max_length=50)
    primary_parent_email = models.EmailField('Email', max_length=254)
    primary_parent_phone_number = PhoneNumberField('Phone Number')
    secondary_parent_first_name = models.CharField('First Name', max_length=50, blank=True)
    secondary_parent_last_name = models.CharField('Last Name', max_length=50, blank=True)
    secondary_parent_email = models.EmailField('Email', max_length=254, blank=True)
    secondary_parent_phone_number = PhoneNumberField('Phone Number', blank=True)
    street = models.CharField(max_length=50)
    suite = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    # TODO: normalize names

    def __str__(self):
        return '%s %s' % (self.primary_parent_first_name, self.primary_parent_last_name)

    class Meta:
        managed=False
        verbose_name_plural = "families"
        ordering = ['primary_parent_first_name', 'primary_parent_last_name']

        def __unicode__(self):
            return self.title


class Camper(models.Model):
    GENDER_CHOICES = (
        (0, 'Male'),
        (1, 'Female'),
    )
    STATUS_CHOICES = (
        (0, 'Active'),
        (1, 'Graduated'),
    )
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birthdate = models.DateField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    email = models.EmailField(max_length=254, blank=True)
    medical_conditions_and_medication = models.TextField()
    diet_and_food_allergies = models.TextField()
    returning = models.BooleanField()
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def preregister(self):
        ordered_regs = self.registration_set.order_by('camp__year')
        current_camp = Camp.objects.last()
        if self.status != 0:
            raise InactiveCamper(self.full_name)
        elif ordered_regs.last().camp.year == current_camp.year:
            raise RegistrationAlreadyExists(self.full_name, current_camp.year)
        else:
            # copy last registration and update grade
            last_reg = ordered_regs.last()
            last_reg.pk = None
            last_reg.status = 0
            last_reg.preregistration = True
            last_reg.grade = min(12, last_reg.grade + (int(current_camp.year) - int(last_reg.camp.year)))
            last_reg.camp = current_camp
            last_reg.additional_shirts = {}
            last_reg.save()
            return last_reg


    def get_registration_links_list(self):
        return format_html_join(
                ', ', '<a href="{}">{}</a>',
                ((reverse('admin:bahtzang_registration_change', args=(r.id,)),
                    r.camp.year) for r in self.registration_set.all())
            )
    get_registration_links_list.short_description = 'Registrations'

    def clean_fields(self, exclude=None):
        # TODO: normalize names
        super().clean_fields(exclude=exclude)
        # verify that birthdate is within 5-20 years ago
        if (self.birthdate.year <= timezone.now().year-20) | (self.birthdate.year >= timezone.now().year-5):
            raise ValidationError(
                _('Birthdate is not within the accepted range.')
            )

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)


    def __str__(self):
        return self.full_name

    class Meta:
        managed=False
        ordering = ['first_name', 'last_name']

        def __unicode__(self):
            return self.title


class Registration_Payment(models.Model):
    PAYMENT_METHODS = (
        (0, 'Stripe'),
        (1, 'Check'),
        (2, 'Cash'),
    )
    breakdown = models.TextField()
    additional_donation = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    discount_code = models.CharField(max_length=50, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_charge_id = models.CharField(max_length=50, blank=True)
    stripe_brand = models.CharField(max_length=50, blank=True)
    stripe_last_four = models.CharField(max_length=4, blank=True)
    payment_method = models.IntegerField(choices = PAYMENT_METHODS)
    check_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.payment_method == 0:
            if !(stripe_charge_id && stripe_brand && stripe_last_four):
                raise ValidationError(
                    _('Missing card information.')
                )
        elif self.payment_method == 1:
            if self.check_number is None:
                raise ValidationError(
                    _('Missing check information.')
                )

    # TODO: verify numericality of stripe_last_four

    def get_registration_links_list(self):
        return format_html_join(
            ', ', '<a href="{}">{} ({})</a>',
            ((reverse('admin:bahtzang_registration_change', args=(r.id,)),
                r.camper.full_name, r.camp.year) for r in self.registration_set.all())
        )
    get_registration_links_list.short_description = 'Registrations'

    def get_stripe_link(self):
        return format_html(
            '<a href="https://dashboard.stripe.com/payments/{}" target="_blank">Open in Stripe</a>',
            self.stripe_charge_id,
        )
    get_stripe_link.short_description = 'Stripe Link'

    def __str__(self):
        return 'RP#{}'.format(self.id)

    class Meta:
        # managed=False
        verbose_name = 'Registration Payment'

        def __unicode__(self):
            return self.title


class Registration(models.Model):
    SHIRT_SIZES = (
        (0, 'X-Small'),
        (1, 'Small'),
        (2, 'Medium'),
        (3, 'Large'),
        (4, 'X-Large'),
        (5, 'XX-Large'),
    )
    STATUS_CHOICES = (
        (0, 'Active'),
        (1, 'Cancelled'),
        (2, 'Waitlisted'),
    )
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    camper = models.ForeignKey(Camper, on_delete=models.CASCADE)
    registration_payment = models.ForeignKey(Registration_Payment,on_delete=models.CASCADE, blank=True)
    grade = models.IntegerField(validators=[MinValueValidator(3), MaxValueValidator(12)])
    shirt_size = models.IntegerField(choices=SHIRT_SIZES, blank=True)
    additional_shirts = JSONField(blank=True)
    bus = models.BooleanField()
    jtasa_chapter = models.CharField(max_length=50, blank=True)
    camper_involvement = JSONField(blank=True)
    additional_notes = models.TextField(blank=True)
    waiver_signature = models.CharField(max_length=100, blank=True)
    waiver_date = models.DateField(blank=True)
    preregistration = models.BooleanField(default=False)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    group = models.IntegerField(blank=True)
    camp_family = models.CharField(max_length=100, blank=True)
    cabin = models.CharField(max_length=50, blank=True)
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    created_at = models.DateTimeField('Registered', auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)

        # copy city and state from family
        self.city = self.camper.family.city
        self.state = self.camper.family.state

        # on create only
        if not self.pk:
            # verify that waiver signature matches primary parent name
            if self.waiver_signature:
                parent_name = self.camper.family.__str__().lower()
                if self.waiver_signature.lower() != parent_name:
                    raise ValidationError(
                        _('Waiver signature does not seem to match parent name.')
                    )
            # verify that waiver date is within today +/- 1
            if self.waiver_date:
                current_date = timezone.now().date()
                if (self.waiver_date <= current_date + timezone.timedelta(days=-1)) | (self.waiver_date >= current_date + timezone.timedelta(1)):
                    raise ValidationError(
                        _('Waiver date does not match current date.')
                    )

    def get_additional_shirts(self):
        self.additional_shirts

    def __str__(self):
        return '%s (%d)' % (str(self.camper), self.camp.year)

    class Meta:
        managed=False

        def __unicode__(self):
            return self.title


class Registration_Discount(models.Model):
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    registration_payment = models.ForeignKey(Registration_Payment, on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    discount_percent = models.IntegerField()
    redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        # remove spaces from discount code
        self.code = self.code.replace(" ", "").upper()
        # toggle redeemed if payement exists
        if self.registration_payment:
            self.redeemed = True
        else:
            self.redeemed = False

    def __str__(self):
        return self.code

    class Meta:
        managed=False
        verbose_name = 'Registration Discount'

        def __unicode__(self):
            return self.title


class Last_Day_Purchase(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = PhoneNumberField(blank=True)
    camper_names = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=9)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    dollar_for_dollar = models.BooleanField()
    company = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=50)
    stripe_brand = models.CharField(max_length=50)
    stripe_last_four = models.CharField(max_length=4)
    # created_at = models.DateTimeField()
    # updated_at = models.DateTimeField()

    # TODO: verify numericality of stripe_last_four

    def get_stripe_link(self):
        return format_html(
            '<a href="https://dashboard.stripe.com/payments/{}" target="_blank">Open in Stripe</a>',
            self.stripe_charge_id,
        )
    get_stripe_link.short_description = 'Stripe Link'

    def __str__(self):
        return f"#{self.id} - {self.email}"

    class Meta:
        managed=False
        verbose_name = 'Last Day Purchase'

        def __unicode__(self):
            return self.title


class Donation(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = PhoneNumberField(blank=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=9)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    company_match = models.BooleanField()
    company = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=50)
    stripe_brand = models.CharField(max_length=50)
    stripe_last_four = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    # TODO: verify numericality of stripe_last_four

    def get_stripe_link(self):
        return format_html(
            '<a href="https://dashboard.stripe.com/payments/{}" target="_blank">Open in Stripe</a>',
            self.stripe_charge_id,
        )
    get_stripe_link.short_description = 'Stripe Link'

    def __str__(self):
        return f"Donation from {self.first_name} {self.last_name}"

    class Meta:
        managed=False

        def __unicode__(self):
            return self.title


class Referral_Method(models.Model):
    name = models.CharField(max_length=100)
    allow_details = models.BooleanField()
    details_field_label = models.CharField(max_length=255, default="Please specify:", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        managed=False
        verbose_name = 'Referral Method'

        def __unicode__(self):
            return self.title


class Referral(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    referral_method = models.ForeignKey(Referral_Method, on_delete=models.CASCADE)
    details = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"{self.family} - {self.referral_method}"

    class Meta:
        managed=False

        def __unicode__(self):
            return self.title
