from policyengine_us.model_api import *


class ut_taxpayer_credit_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah initial taxpayer credit"
    unit = USD
    documentation = "Form TC-40, line (12 through) 16"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        deductions = add(
            tax_unit,
            period,
            [
                "ut_personal_exemption",
                "ut_federal_deductions_for_taxpayer_credit",
            ],
        )
        rate = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.rate
        # The exemption is not actually applied here in the form, but we include it here
        # to avoid counting the exemption as a nonrefundable credit when comparing against
        # ut_income_tax_before_credits.
        return rate * deductions
