from openfisca_us.model_api import *


class aged_blind_extra_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Aged and blind standard deduction"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        std = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("filing_status", period)
        filing_status_type = filing_status.possible_values
        blind_head = tax_unit("blind_head", period) * 1
        blind_spouse = tax_unit("blind_spouse", period) * 1
        aged_head = (
            tax_unit("age_head", period) >= std.aged_or_blind.age_threshold
        ) * 1
        aged_spouse = (
            (filing_status == filing_status_type.JOINT)
            & (
                tax_unit("age_spouse", period)
                >= std.aged_or_blind.age_threshold
            )
        ) * 1
        count_extra_stded = blind_head + blind_spouse + aged_head + aged_spouse
        return count_extra_stded * std.aged_or_blind.amount[filing_status]
