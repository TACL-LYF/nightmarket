from django.db import models
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.contrib.postgres.fields import JSONField

class Camp(models.Model):
    year = models.IntegerField()
    name = models.CharField(max_length=100)
    campsite = models.CharField(max_length=100)
    campsite_address = models.CharField(max_length=100)
    camp_start_date = models.DateField()
    camp_end_date = models.DateField()
    registration_open_date = models.DateField()
    registration_late_date = models.DateField()
    registration_close_date = models.DateField()
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2)
    shirt_price = models.DecimalField(max_digits=6, decimal_places=2)
    sibling_discount = models.DecimalField(max_digits=6, decimal_places=2)
    registration_late_fee = models.DecimalField(max_digits=6, decimal_places=2)
    waitlist_starts_after = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    primary_parent_phone_number = models.CharField('Phone Number', max_length=10)
    secondary_parent_first_name = models.CharField('First Name', max_length=50)
    secondary_parent_last_name = models.CharField('Last Name', max_length=50)
    secondary_parent_email = models.EmailField('Email', max_length=254)
    secondary_parent_phone_number = models.CharField('Phone Number', max_length=10)
    street = models.CharField(max_length=50)
    suite = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=9)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    email = models.EmailField(max_length=254)
    medical_conditions_and_medication = models.TextField()
    diet_and_food_allergies = models.TextField()
    returning = models.BooleanField()
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def get_registration_links_list(self):
        return format_html_join(
                ', ', '<a href="{}">{}</a>',
                ((reverse('admin:bahtzang_registration_change', args=(r.id,)),
                    r.camp.year) for r in self.registration_set.all())
            )
    get_registration_links_list.short_description = 'Registrations'

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
    breakdown = models.TextField()
    additional_donation = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_charge_id = models.CharField(max_length=50)
    stripe_brand = models.CharField(max_length=50)
    stripe_last_four = models.CharField(max_length=4)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
        return 'RP#%d' % (self.id)

    class Meta:
        managed=False
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
    registration_payment = models.ForeignKey(Registration_Payment, on_delete=models.CASCADE)
    grade = models.IntegerField()
    shirt_size = models.IntegerField(choices=SHIRT_SIZES)
    additional_shirts = JSONField(blank=True)
    bus = models.BooleanField()
    jtasa_chapter = models.CharField(max_length=50, blank=True)
    camper_involvement = models.TextField()
    additional_notes = models.TextField(blank=True)
    waiver_signature = models.CharField(max_length=100)
    waiver_date = models.DateField()
    preregistration = models.BooleanField(default=False)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    group = models.IntegerField(blank=True)
    camp_family = models.CharField(max_length=100, blank=True)
    cabin = models.CharField(max_length=50, blank=True)
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    created_at = models.DateTimeField('Registered')
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.code

    class Meta:
        managed=False
        verbose_name = 'Registration Discount'

        def __unicode__(self):
            return self.title


class Registration_Session(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed=False

        def __unicode__(self):
            return self.title


class Last_Day_Purchase(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=10)
    camper_names = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=9)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    dollar_for_dollar = models.BooleanField()
    company = models.CharField(max_length=100)
    stripe_charge_id = models.CharField(max_length=50)
    stripe_brand = models.CharField(max_length=50)
    stripe_last_four = models.CharField(max_length=4)
    # created_at = models.DateTimeField()
    # updated_at = models.DateTimeField()

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
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=9)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    company_match = models.BooleanField()
    company = models.CharField(max_length=100)
    stripe_charge_id = models.CharField(max_length=50)
    stripe_brand = models.CharField(max_length=50)
    stripe_last_four = models.CharField(max_length=4)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    details = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.family} - {self.referral_method}"

    class Meta:
        managed=False

        def __unicode__(self):
            return self.title
