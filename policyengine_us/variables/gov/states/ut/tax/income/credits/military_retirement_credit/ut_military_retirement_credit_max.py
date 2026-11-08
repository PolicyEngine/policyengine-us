from policyengine_us.model_api import *


class ut_military_retirement_credit_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah military retirement credit maximum amount"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1043.html"
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        # 59-10-1043(2)(b): only the pay included in adjusted gross income on
        # the claimant's federal return, which excludes dependents' income;
        # dependents report it on their own return.
        military_retirement_pay = tax_unit_non_dep_add(
            tax_unit,
            period,
            ["military_retirement_income"],
        )
        # 59-10-1043(2)(a): the percentage listed in 59-10-104(2), the
        # income tax rate.
        p = parameters(period).gov.states.ut.tax.income
        in_effect = p.credits.military_retirement.in_effect
        return in_effect * military_retirement_pay * p.rate
