from policyengine_us.model_api import *


class id_aged_or_disabled_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Idaho aged or disabled credit"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.subtractions.aged_or_disabled
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        # Aged eligible individuals cannot be the head or spouse.
        age_eligible = (age >= p.age_threshold) & ~head_or_spouse
        # Disabled eligible individuals can include head and spouse.
        disabled_eligible = person("is_disabled", period)
        # To claim aged or disabled credit, filers also have to maintain a household for family members
        # and provide more than one-half of the family member’s support for the year
        support_payment_ratio = person(
            "share_of_care_and_support_costs_paid_by_tax_filer", period
        )
        payment_eligible = support_payment_ratio > p.support_fraction_threshold
        return (age_eligible | disabled_eligible) & payment_eligible
