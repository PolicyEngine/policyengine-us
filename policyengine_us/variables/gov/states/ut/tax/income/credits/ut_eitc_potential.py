from policyengine_us.model_api import *


class ut_eitc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Earned Income Tax Credit"
    unit = USD
    documentation = "This credit is a fraction of the federal EITC."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1044.html?v=C59-10-S1044_2022050420220504"

    def formula(tax_unit, period, parameters):
        # Utah Code § 59-10-1044 caps the credit at W-2 state wages
        # (Box 16 per TC-40A worksheet), explicitly excluding self-employment
        # earnings. W-2 Box 1 (irs_employment_income) is used as a proxy
        # because PolicyEngine does not expose a state-wages variable; for
        # most filers Box 16 and Box 1 are identical.
        p = parameters(period).gov.states.ut.tax.income.credits.earned_income
        federal_eitc = tax_unit("eitc", period)
        wages = add(tax_unit, period, ["irs_employment_income"])
        return min_(p.rate * federal_eitc, wages)
