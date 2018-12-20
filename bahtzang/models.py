from django.db import models


# TODO: FOREIGN KEYS TO BE UPDATED
# add_foreign_key "campers", "campers", column: "possible_dupe_of_id"
# add_foreign_key "campers", "families"
# add_foreign_key "referrals", "families"
# add_foreign_key "referrals", "referral_methods"
# add_foreign_key "registration_discounts", "camps"
# add_foreign_key "registration_discounts", "registration_payments"
# add_foreign_key "registrations", "campers"
# add_foreign_key "registrations", "camps"
# add_foreign_key "registrations", "registration_payments"


class Registration(models.Model):
    grade = models.IntegerField()
    shirt_size = models.CharField()
    bus = models.BooleanField()
    additional_notes = models.TextField()
    waiver_signature = models.CharField()
    group = models.IntegerField()
    camp_family = models.CharField()
    cabin = models.CharField()
    city = models.CharField()
    state = models.CharField()
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    camper = models.ForeignKey(Camper, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    additional_shirts = models.TextField()
    registration_payment_id = models.IntegerField()
    camper_involvement = models.TextField()
    jtasa_chapter = models.CharField()
    preregistration = models.BooleanField(default=False)
    status = models.IntegerField(default=0)

    class Meta:
        ordering = ['created_on']

        def __unicode__(self):
            return self.title


class Registration_Payment(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    additional_donation = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField()
    stripe_charge_id = models.CharField()
    breakdown = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    stripe_brand = models.CharField()
    stripe_last_four = models.IntegerField()

    class Meta:
        ordering = ['stripe_charge_id']

        def __unicode__(self):
            return self.title


class Registration_Discount(models.Model):
    code = models.CharField()
    discount_percent = models.IntegerField()
    redeemed = models.BooleanField(default=False)
    camp = models.IntegerField()
    registration_payment_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Registration_Session(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Last_Day_Purchase(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    email = models.CharField()
    phone = models.CharField()
    address = models.CharField()
    city = models.CharField()
    state = models.CharField()
    zip = models.CharField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    company_match = models.BooleanField()
    company = models.CharField()
    stripe_charge_id = models.CharField()
    stripe_brand = models.CharField()
    stripe_last_four = models.CharField()
    camper_names = models.CharField()


class Donation(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    email = models.CharField()
    phone = models.CharField()
    address = models.CharField()
    city = models.CharField()
    state = models.CharField()
    zip = models.CharField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    company_match = models.BooleanField()
    company = models.CharField()
    stripe_charge_id = models.CharField()
    stripe_brand = models.CharField()
    stripe_last_four = models.CharField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Camp(models.Model):
    name = models.CharField()
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
    campsite = models.CharField()
    campsite_address = models.CharField()

    class Meta:
        ordering = ['year']

        def __unicode__(self):
            return self.title


class Camper(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    birthdate = models.DateTimeField()
    gender = models.IntegerField()
    email = models.CharField()
    medical_conditions_and_medication = models.TextField()
    diet_and_food_allergies = models.TextField()
    status = models.IntegerField(default=0)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    returning = models.BooleanField()
    possible_dupe_of_id = models.IntegerField()

    class Meta:
        ordering = ['first_name', 'last_name']

        def __unicode__(self):
            return self.title


class Family(models.Model):
    primary_parent_first_name = models.CharField()
    primary_parent_last_name = models.CharField()
    primary_parent_email = models.CharField()
    primary_parent_phone_number = models.CharField()
    secondary_parent_first_name = models.CharField()
    secondary_parent_last_name = models.CharField()
    secondary_parent_email = models.CharField()
    secondary_parent_phone_number = models.CharField()
    suite = models.CharField()
    street = models.CharField()
    city = models.CharField()
    state = models.CharField()
    zip = models.CharField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        ordering = ['primary_parent_first_name', 'primary_parent_last_name']

        def __unicode__(self):
            return self.title


class Referral_Method(models.Model):
    name = models.CharField()
    allow_details = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Referral(models.Model):
    details = models.CharField()
    family = models.ForeignKey(Family, on_delete=CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    referral_method_id = family = models.ForeignKey(Referral_Method, on_delete=CASCADE)
