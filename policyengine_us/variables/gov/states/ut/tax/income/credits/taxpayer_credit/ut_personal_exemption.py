from policyengine_us.model_api import *


class ut_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah personal exemption"
    unit = USD
    defined_for = StateCode.UT
    documentation = "Form TC-40, line 11"
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"

    def formula(tax_unit, period, parameters):
        ut_total_dependents = tax_unit("ut_total_dependents", period)
        rate = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.personal_exemption
        return rate * ut_total_dependents
