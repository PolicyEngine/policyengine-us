from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class basic_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        STD = parameters(period).tax.deductions.standard
        MARS = tax_unit("MARS", period)
        MIDR = tax_unit("MIDR", period)

        c15100_if_DSI = max_(
            STD.dependent.additional_earned_income
            + tax_unit("earned", period),
            STD.dependent.amount,
        )
        basic_if_DSI = min_(STD.amount[MARS], c15100_if_DSI)
        basic_if_not_DSI = where(MIDR, 0, STD.amount[MARS])
        basic_stded = where(
            tax_unit("DSI", period), basic_if_DSI, basic_if_not_DSI
        )
        return basic_stded


class aged_blind_extra_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Aged and blind standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        STD = parameters(period).tax.deductions.standard
        MARS = tax_unit("MARS", period)
        MARSType = MARS.possible_values
        num_extra_stded = (
            tax_unit("blind_head", period) * 1
            + tax_unit("blind_spouse", period) * 1
            + (tax_unit("age_head", period) >= STD.aged_or_blind.age_threshold)
            * 1
            + (
                (MARS == MARSType.JOINT)
                & (
                    tax_unit("age_spouse", period)
                    >= STD.aged_or_blind.age_threshold
                )
            )
            * 1
        )
        extra_stded = num_extra_stded * STD.aged_or_blind.amount[MARS]
        return extra_stded


class standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Calculate basic standard deduction
        basic_stded = tax_unit("basic_standard_deduction", period)
        CHARITY = parameters(period).tax.deductions.itemized.charity
        MARS = tax_unit("MARS", period)
        MIDR = tax_unit("MIDR", period)
        MARSType = MARS.possible_values

        # Calculate extra standard deduction for aged and blind
        extra_stded = tax_unit("aged_blind_extra_standard_deduction", period)

        # Calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((MARS == MARSType.SEPARATE) & MIDR, 0, standard)
        standard += CHARITY.allow_nonitemizers * min_(
            tax_unit("c19700", period), CHARITY.nonitemizers_max
        )

        return standard


class sey_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "e00900p", "e02100p", "k1bx14p")


class sey_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "e00900s", "e02100ps", "k1bx14s")


class sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "sey_p", "sey_s")


class earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(
            0,
            add(tax_unit, period, "e00200p", "e00200s", "sey")
            - tax_unit("c03260", period),
        )


class TaxInc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # not accurate, for demo
        return max_(
            0,
            tax_unit("earned", period)
            - tax_unit("standard_deduction", period),
        )


class income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # not accurate, for demo
        return tax_unit("TaxInc", period)


class Taxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("income", period)
        MARS = tax_unit("MARS", period)
        brackets = parameters(period).tax.income.bracket
        thresholds = (
            [0]
            + [brackets.thresholds[str(i)][MARS] for i in range(1, 7)]
            + [infinity]
        )
        rates = [brackets.rates[str(i)] for i in range(1, 8)]
        bracketed_amounts = [
            amount_between(income, lower, upper)
            for lower, upper in zip(thresholds[:-1], thresholds[1:])
        ]
        bracketed_tax_amounts = [
            rates[i] * bracketed_amounts[i] for i in range(7)
        ]
        tax_amount = sum(bracketed_tax_amounts)
        return tax_amount


class AfterTaxIncome(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("earned", period) - tax_unit("Taxes", period)
