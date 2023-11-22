from policyengine_us.model_api import *


class id_aged_or_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho aged or disabled credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # The program includes individuals in the household, including those not in the filing unit.
        # We simplify by limiting to those in the filing unit.
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.id.tax.income.credits.aged_or_disabled
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Aged-eligible individuals cannot be head or spouse.
        age_eligible = (age >= p.age_threshold) & ~head_or_spouse
        # Disabled-eligible individuals can include head and spouse.
        disabled_eligible = person("is_disabled", period)
        # To claim aged or disabled credit, filers also have to maintain a household for family members
        # and provide more than one-half of the family member’s support for the year
        support_payment_ratio = person(
            "share_of_care_and_support_costs_paid_by_tax_filer", period
        )
        payment_eligible = support_payment_ratio > p.support_fraction_threshold
        eligible_person = (age_eligible | disabled_eligible) & payment_eligible
        total_eligible_people = sum(eligible_person)
        capped_eligible_people = min_(total_eligible_people, p.person_cap)
        credit_amount = capped_eligible_people * p.amount
        selected_credit = tax_unit(
            "id_selected_aged_or_disabled_credit", period
        )
        return where(selected_credit, credit_amount, 0)
