from policyengine_us.model_api import *


class il_base_income_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        # Illinois adds these items to federal adjusted gross income, which
        # leaves out a tax unit dependent's income (the dependent files their
        # own return), so only the head's and spouse's amounts count, such as
        # their federally tax-exempt interest (IL-1040 line 2).
        p = parameters(period).gov.states.il.tax.income.base
        return tax_unit_non_dep_add(tax_unit, period, p.additions)
