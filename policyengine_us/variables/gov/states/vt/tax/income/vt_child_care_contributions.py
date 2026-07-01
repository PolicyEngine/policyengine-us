from policyengine_us.model_api import *


class vt_child_care_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child care contributions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.child_care_contributions
        if p.applies:
            # The Child Care Contribution Worksheet applies the rate to net
            # earnings from self-employment (federal Schedule SE, Line 6),
            # i.e. taxable_self_employment_income, not gross self-employment
            # income.
            income = add(tax_unit, period, ["taxable_self_employment_income"])
            applicable_income = max_(0, income) * p.rate.income
            return applicable_income * p.rate.contributions
        return 0
