from openfisca_us.model_api import *


class basic_income_before_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income before phase-outs"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).contrib.ubi_center.basic_income
        # Start with person-level amount.
        person = tax_unit.members
        age = person("age", period)
        amount = p.amount_by_age.calc(age)
        person_level_amount = tax_unit.sum(amount)
        # Now compute FPG amount.
        fpg = tax_unit("tax_unit_fpg", period)
        fpg_amount = p.fpg_percent * fpg
        return person_level_amount + fpg_amount
