from openfisca_core.model_api import *
from openfisca_us.entities import *

class DSI(Variable):
    value_type = bool
    entity = TaxUnit
    label = u'Whether claimed as a dependent on another return'
    definition_period = YEAR

class earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = u'Earned income for filing unit'
    definition_period = YEAR

class age_head(Variable):
    value_type = int
    entity = TaxUnit
    label = u'Age in years of the taxpayer'
    definition_period = YEAR

class age_spouse(Variable):
    value_type = int
    entity = TaxUnit
    label = u'Age in years of the spouse'
    definition_period = YEAR

class MIDR(Variable):
    value_type = bool
    entity = TaxUnit
    label = u'Whether the separately filing spouse itemizes'
    definition_period = YEAR

class blind_head(Variable):
    value_type = bool
    entity = TaxUnit
    label = u'Whether the taxpayer is blind'
    definition_period = YEAR

class blind_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    label = u'Whether the spouse is blind'
    definition_period = YEAR

class c19700(Variable):
    value_type = float
    entity = TaxUnit
    label = u'Schedule A: charitable contributions deducted'
    definition_period = YEAR

class standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = u'Standard deduction, including for dependents, aged and blind'
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # calculate basic standard deduction

        STD = parameters(period).tax.deductions.standard
        MARS = taxunit("MARS", period)
        MIDR = taxunit("MIDR", period)
        MARSType = MARS.possible_values
        c15100_if_DSI = max_(350 + taxunit("earned_income", period), STD.amount.dependent)
        basic_if_DSI = min_(STD.amount.filer[MARS], c15100_if_DSI)
        basic_if_not_DSI = where(MIDR, 0, STD.amount.filer[MARS])
        basic_stded = where(taxunit("DSI", period), basic_if_DSI, basic_if_not_DSI)

        # calculate extra standard deduction for aged and blind
        num_extra_stded = taxunit("blind_head", period) * 1 + taxunit("blind_spouse", period) * 1
        extra_joint_multiplier = where(MARS == MARSType.JOINT, 2, 1)
        num_extra_stded += (taxunit("age_head", period) >= 65) * extra_joint_multiplier
        extra_stded = num_extra_stded * STD.amount.aged_or_blind[MARS]

        # calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((MARS == MARSType.SEPARATE) & MIDR, 0, standard)
        standard += STD.charity.allow_nonitemizers * min_(taxunit("c19700", period), STD.charity.nonitemizers_max)

        return standard
