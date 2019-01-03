from django.db import models

class Camp(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2)
    shirt_price = models.DecimalField(max_digits=6, decimal_places=2)
    sibling_discount = models.DecimalField(max_digits=6, decimal_places=2)
    registration_late_fee = models.DecimalField(max_digits=6, decimal_places=2)
    registration_open_date = models.DateTimeField()
    registration_late_date = models.DateTimeField()
    registration_close_date = models.DateTimeField()
    camp_start_date = models.DateTimeField()
    camp_end_date = models.DateTimeField()
    campsite = models.CharField(max_length=100)
    campsite_address = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.year}: {self.name}"

    class Meta:
        managed = False
        ordering = ['year']

        def __unicode__(self):
            return self.title


class Family(models.Model):
    primary_parent_first_name = models.CharField(max_length=50)
    primary_parent_last_name = models.CharField(max_length=50)
    primary_parent_email = models.CharField(max_length=254)
    primary_parent_phone_number = models.CharField(max_length=10)
    secondary_parent_first_name = models.CharField(max_length=50)
    secondary_parent_last_name = models.CharField(max_length=50)
    secondary_parent_email = models.CharField(max_length=254)
    secondary_parent_phone_number = models.CharField(max_length=10)
    suite = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=9)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.primary_parent_first_name} {self.primary_parent_last_name}"

    class Meta:
        managed = False
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
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birthdate = models.DateTimeField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    email = models.CharField(max_length=254)
    medical_conditions_and_medication = models.TextField()
    diet_and_food_allergies = models.TextField()
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    returning = models.BooleanField()
    possible_dupe_of_id = models.IntegerField()

    def __str__(self):
        managed = False
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['first_name', 'last_name']

        def __unicode__(self):
            return self.title


class Registration_Payment(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    additional_donation = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField(max_length=50)
    stripe_charge_id = models.CharField(max_length=50)
    breakdown = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    stripe_brand = models.CharField(max_length=50)
    stripe_last_four = models.CharField(max_length=4)

    class Meta:
        managed = False

        def __unicode__(self):
            return self.title


class Registration(models.Model):
    SHIRT_SIZES = (
        ('XS', 'X-Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'X-Large'),
        ('2XL', 'XX-Large'),
    )
    STATUS_CHOICES = (
        (0, 'Active'),
        (1, 'Cancelled'),
        (2, 'Waitlisted'),
    )
    grade = models.IntegerField()
    shirt_size = models.CharField(max_length=2, choices=SHIRT_SIZES)
    bus = models.BooleanField()
    additional_notes = models.TextField()
    waiver_signature = models.CharField(max_length=100)
    group = models.IntegerField()
    camp_family = models.CharField(max_length=100)
    cabin = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    camper = models.ForeignKey(Camper, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    additional_shirts = models.TextField()
    registration_payment = models.ForeignKey(Registration_Payment, on_delete=models.CASCADE)
    camper_involvement = models.TextField()
    jtasa_chapter = models.CharField(max_length=50)
    preregistration = models.BooleanField(default=False)
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.camper} ({self.camp.year})"

    class Meta:
        managed = False

        def __unicode__(self):
            return self.title


class Registration_Discount(models.Model):
    code = models.CharField(max_length=50)
    discount_percent = models.IntegerField()
    redeemed = models.BooleanField(default=False)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    registration_payment = models.ForeignKey(Registration_Payment, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.code

    class Meta:
        managed = False

        def __str__(self):
            return self.title


class Registration_Session(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False

        def __unicode__(self):
            return self.title


class Last_Day_Purchase(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=254)
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
    camper_names = models.CharField(max_length=100)

    class Meta:
        managed = False

        def __unicode__(self):
            return self.title


class Donation(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=254)
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

    class Meta:
        managed = False

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
        managed = False

        def __unicode__(self):
            return self.title


class Referral(models.Model):
    details = models.CharField(max_length=100)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    referral_method = models.ForeignKey(Referral_Method, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.family} - {self.referral_method}"

    class Meta:
        managed = False

        def __unicode__(self):
            return self.title
