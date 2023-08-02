from policyengine_us.model_api import *


class de_additional_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware additional standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://delcode.delaware.gov/title30/c011/sc02/index.html#1108"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.deductions.standard.additional

        age_head = tax_unit("age_head", period)
        aged_head_eligible = (age_head >= p.age_threshold).astype(int)

        age_spouse = tax_unit("age_spouse", period)
        aged_spouse_eligible = (age_spouse >= p.age_threshold).astype(int)

        blind_head = tax_unit("blind_head", period)
        blind_head_eligible = (blind_head).astype(int)

        blind_spouse = tax_unit("blind_spouse", period)
        blind_spouse_eligible = (blind_spouse).astype(int)

        return (
            aged_head_eligible
            + aged_spouse_eligible
            + blind_head_eligible
            + blind_spouse_eligible
        ) * p.amount
