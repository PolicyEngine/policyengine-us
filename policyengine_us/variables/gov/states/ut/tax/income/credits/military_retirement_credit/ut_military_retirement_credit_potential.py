from policyengine_us.model_api import *


class ut_military_retirement_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah military retirement credit"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1043.html"
    defined_for = "ut_military_retirement_credit_eligible"

    def formula(tax_unit, period, parameters):
        # 59-10-1043(2)(b): only the pay included in adjusted gross income on
        # the claimant's federal return, which excludes dependents' income;
        # dependents report it on their own return.
        military_retirement_pay = tax_unit_non_dep_sum(
            "military_retirement_pay", tax_unit, period
        )
        p = parameters(period).gov.states.ut.tax.income.credits.military_retirement
        return military_retirement_pay * p.rate
