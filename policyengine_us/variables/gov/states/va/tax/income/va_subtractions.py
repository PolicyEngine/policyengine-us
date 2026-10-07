from policyengine_us.model_api import *


class va_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia subtractions from the adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions
        # Virginia subtracts these items from federal adjusted gross income,
        # which leaves out a tax unit dependent's income (the dependent files
        # their own return), so only the head's and spouse's amounts count.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
