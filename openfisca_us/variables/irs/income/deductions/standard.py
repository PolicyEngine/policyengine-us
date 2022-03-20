from openfisca_us.model_api import *


class basic_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic standard deduction"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        std = parameters(period).irs.deductions.standard
        mars = tax_unit("mars", period)
        midr = tax_unit("midr", period)

        c15100_if_dsi = max_(
            std.dependent.additional_earned_income
            + tax_unit("filer_earned", period),
            std.dependent.amount,
        )
        basic_if_dsi = min_(std.amount[mars], c15100_if_dsi)
        basic_if_not_dsi = where(midr, 0, std.amount[mars])
        return where(tax_unit("dsi", period), basic_if_dsi, basic_if_not_dsi)


class aged_blind_extra_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Aged and blind standard deduction"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        std = parameters(period).irs.deductions.standard
        mars = tax_unit("mars", period)
        mars_type = mars.possible_values
        blind_head = tax_unit("blind_head", period) * 1
        blind_spouse = tax_unit("blind_spouse", period) * 1
        aged_head = (
            tax_unit("age_head", period) >= std.aged_or_blind.age_threshold
        ) * 1
        aged_spouse = (
            (mars == mars_type.JOINT)
            & (
                tax_unit("age_spouse", period)
                >= std.aged_or_blind.age_threshold
            )
        ) * 1
        num_extra_stded = blind_head + blind_spouse + aged_head + aged_spouse
        return num_extra_stded * std.aged_or_blind.amount[mars]


class standard(Variable):
    value_type = float
    entity = TaxUnit
    label = "Standard deduction (zero for itemizers)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        # Calculate basic standard deduction
        basic_stded = tax_unit("basic_standard_deduction", period)
        charity = parameters(period).irs.deductions.itemized.charity
        mars = tax_unit("mars", period)
        midr = tax_unit("midr", period)
        mars_type = mars.possible_values

        # Calculate extra standard deduction for aged and blind
        extra_stded = tax_unit("aged_blind_extra_standard_deduction", period)

        # Calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((mars == mars_type.SEPARATE) & midr, 0, standard)
        return standard + charity.allow_nonitemizers * min_(
            tax_unit("c19700", period), charity.nonitemizers_max
        )
