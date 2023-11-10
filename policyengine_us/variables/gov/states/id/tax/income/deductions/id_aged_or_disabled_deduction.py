from policyengine_us.model_api import *


class id_aged_or_disabled_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho aged or disabled deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled = person("is_disabled", period)
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.aged_or_disabled
        age_eligible = (age >= p.age_eligibility) & ~head_or_spouse
        # To claim aged or disabled credit, filers also have to maintain a household for family members
        # and provide more than one-half of the family member’s support for the year
        care_and_support_payment = person("care_and_support_payment", period)
        care_and_support_costs = person("care_and_support_costs", period)
        support_payment_ratio = np.zeros_like(care_and_support_costs)
        mask = care_and_support_costs != 0
        support_payment_ratio[mask] = (
            care_and_support_payment[mask] / care_and_support_costs[mask]
        )
        payment_eligible = support_payment_ratio > p.cost_rate
        eligible_person = (age_eligible | disabled) & payment_eligible
        total_eligible_people = tax_unit.sum(eligible_person)
        capped_eligible_people = min_(total_eligible_people, p.max_deduction)
        # To claim aged or disabled deduction, filers also have to maintain a household for family members
        # and provide more than one-half of the family member’s support for the year
        return capped_eligible_people * p.amount
