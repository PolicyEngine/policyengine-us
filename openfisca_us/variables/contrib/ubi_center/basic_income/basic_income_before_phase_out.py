from openfisca_us.model_api import *


class basic_income_before_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income before phase-outs"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).contrib.ubi_center.basic_income.amount
        # Start with flat person-level amount.
        total_flat_amount = p.person.flat * tax_unit("tax_unit_size", period)
        # Add per-age person-level amount.
        person = tax_unit.members
        age = person("age", period)
        amount_by_age = p.person.by_age.calc(age)
        total_amount_by_age = tax_unit.sum(amount_by_age)
        # Now compute FPG amount.
        fpg = tax_unit("tax_unit_fpg", period)
        fpg_amount = p.tax_unit.fpg_percent * fpg
        return total_flat_amount + total_amount_by_age + fpg_amount
