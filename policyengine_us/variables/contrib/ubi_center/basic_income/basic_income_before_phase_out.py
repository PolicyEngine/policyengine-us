from policyengine_us.model_api import *


class basic_income_before_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income before phase-outs"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.ubi_center.basic_income
        # Start with flat person-level amount.
        total_flat_amount = p.amount.person.flat * tax_unit(
            "tax_unit_size", period
        )
        # Add per-age person-level amount.
        person = tax_unit.members
        age = person("age", period)
        amount_by_age = p.amount.person.by_age.calc(age)
        total_amount_by_age = tax_unit.sum(amount_by_age)
        # If available, apply a marriage bonus
        married = tax_unit.family("is_married", period)
        marriage_bonus_rate = (
            p.amount.person.marriage_bonus * total_amount_by_age
        )
        post_marriage_bonus_amount = total_amount_by_age + marriage_bonus_rate
        applicable_amount_by_age = where(
            married, post_marriage_bonus_amount, total_amount_by_age
        )
        # Now compute FPG amount.
        fpg = tax_unit("tax_unit_fpg", period)
        fpg_amount = p.amount.tax_unit.fpg_percent * fpg

        # Disability amount
        disabled = person("is_ssi_disabled", period)
        disabled_amount = tax_unit.sum(disabled * p.amount.person.disability)
        base_amount = (
            total_flat_amount
            + applicable_amount_by_age
            + fpg_amount
            + disabled_amount
        )
        if p.phase_in.in_effect:
            phase_in_amount = tax_unit("basic_income_phase_in", period)
            return min_(base_amount, phase_in_amount)
        return base_amount
