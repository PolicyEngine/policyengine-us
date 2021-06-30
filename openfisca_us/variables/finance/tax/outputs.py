from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Standard deduction, including for dependents, aged and blind"
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # calculate basic standard deduction

        STD = parameters(period).tax.deductions.standard
        MARS = taxunit("MARS", period)
        MIDR = taxunit("MIDR", period)
        MARSType = MARS.possible_values
        c15100_if_DSI = max_(
            350 + taxunit("earned", period), STD.amount.dependent
        )
        basic_if_DSI = min_(STD.amount.filer[MARS], c15100_if_DSI)
        basic_if_not_DSI = where(MIDR, 0, STD.amount.filer[MARS])
        basic_stded = where(
            taxunit("DSI", period), basic_if_DSI, basic_if_not_DSI
        )

        # calculate extra standard deduction for aged and blind
        num_extra_stded = (
            taxunit("blind_head", period) * 1
            + taxunit("blind_spouse", period) * 1
        )
        extra_joint_multiplier = where(MARS == MARSType.JOINT, 2, 1)
        num_extra_stded += (
            taxunit("age_head", period) >= 65
        ) * extra_joint_multiplier
        extra_stded = num_extra_stded * STD.amount.aged_or_blind[MARS]

        # calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((MARS == MARSType.SEPARATE) & MIDR, 0, standard)
        standard += STD.charity.allow_nonitemizers * min_(
            taxunit("c19700", period), STD.charity.nonitemizers_max
        )

        return standard


class sey_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return add(taxunit, period, "e00900p", "e02100p", "k1bx14p")


class sey_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return add(taxunit, period, "e00900s", "e02100ps", "k1bx14s")


class sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return add(taxunit, period, "sey_p", "sey_s")


class earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return max_(
            0,
            add(taxunit, period, "e00200p", "e00200s", "sey")
            - taxunit("c03260", period),
        )


class TaxInc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # not accurate, for demo
        return max_(
            0,
            taxunit("earned", period) - taxunit("standard_deduction", period),
        )


class income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # not accurate, for demo
        return taxunit("TaxInc", period)


class Taxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        income = taxunit("income", period)
        MARS = taxunit("MARS", period)
        brackets = parameters(period).tax.income.bracket
        thresholds = (
            [0]
            + [brackets.thresholds[str(i)][MARS] for i in range(1, 7)]
            + [infinity]
        )
        rates = [brackets.rates[str(i)][MARS] for i in range(1, 8)]
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

    def formula(taxunit, period, parameters):
        return taxunit("earned", period) - taxunit("Taxes", period)
