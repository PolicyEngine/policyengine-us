from policyengine_us.model_api import *


class ut_ss_benefits_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Social Security Benefits Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        claims_retirement_credit = tax_unit(
            "ut_claims_retirement_credit", period
        )
        max_credit = tax_unit("ut_ss_benefits_credit_max", period)
        limiting_liability = (
            tax_unit("ut_income_tax_before_credits", period)
            - tax_unit("ut_taxpayer_credit", period)
            - tax_unit("ut_eitc", period)
        )
        if not parameters(
            period
        ).gov.states.ut.tax.income.credits.ss_benefits.refundable:
            return min_(
                ~claims_retirement_credit * max_credit, limiting_liability
            )
        return ~claims_retirement_credit * max_credit
