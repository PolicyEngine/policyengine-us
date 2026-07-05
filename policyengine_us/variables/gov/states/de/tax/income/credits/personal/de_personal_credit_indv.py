from policyengine_us.model_api import *


class de_personal_credit_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware personal credit per person for combined separate filing"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # PIT-RES Line 27a: "split the total between Columns A and
        # B in increments of $110."  The form lets the taxpayer
        # choose any split; we find the optimal split that maximises
        # total credits used (i.e. minimises tax).
        p = parameters(period).gov.states.de.tax.income.credits
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)

        person_tax = person("de_income_tax_before_non_refundable_credits_indv", period)
        head_tax = person.tax_unit.sum(is_head * person_tax)
        spouse_tax = person.tax_unit.sum(is_spouse * person_tax)

        fixed = person("de_aged_personal_credit_indv", period) + person(
            "de_cdcc_indv", period
        )
        head_fixed = person.tax_unit.sum(is_head * fixed)
        spouse_fixed = person.tax_unit.sum(is_spouse * fixed)

        head_capacity = max_(head_tax - head_fixed, 0)
        spouse_capacity = max_(spouse_tax - spouse_fixed, 0)

        credit_per = p.personal_credits.personal
        total_units = person.tax_unit("exemptions_count", period)
        total = credit_per * total_units

        # Optimal split: try proportional floor and ceil, pick
        # whichever maximises effective credits (min of alloc vs
        # capacity in each column).
        total_capacity = head_capacity + spouse_capacity
        ratio = where(total_capacity > 0, head_capacity / total_capacity, 0)

        n_low = np.floor(total_units * ratio)
        n_high = n_low + 1
        n_low = max_(min_(n_low, total_units), 0)
        n_high = max_(min_(n_high, total_units), 0)

        eff_low = min_(n_low * credit_per, head_capacity) + min_(
            (total_units - n_low) * credit_per, spouse_capacity
        )
        eff_high = min_(n_high * credit_per, head_capacity) + min_(
            (total_units - n_high) * credit_per, spouse_capacity
        )

        n_head = where(eff_high > eff_low, n_high, n_low)
        head_alloc = n_head * credit_per
        spouse_alloc = total - head_alloc

        return where(is_head, head_alloc, where(is_spouse, spouse_alloc, 0))
