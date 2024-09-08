from policyengine_us.model_api import *


class ut_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah personal exemption"
    unit = USD
    defined_for = StateCode.UT
    definition_period = YEAR
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323",  # Form TC-40, Line 11
        "https://le.utah.gov/~2023/bills/static/HB0054.html#59-10-1044",  # 59-10-1018 (1)(g)
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.taxpayer
        ut_total_dependents = tax_unit("ut_total_dependents", period)
        if p.in_effect:
            additional_dependents = tax_unit(
                "ut_personal_exemption_additional_dependents", period
            )
            ut_total_dependents += additional_dependents
        rate = p.personal_exemption
        return rate * (ut_total_dependents)
