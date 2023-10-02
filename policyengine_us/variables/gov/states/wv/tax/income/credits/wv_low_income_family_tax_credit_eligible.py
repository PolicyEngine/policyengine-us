from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia low-income family tax credit"
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        # modified agi needed to be modified
        wv_agi = tax_unit("wv_agi", period)
        filing_status = tax_unit("filing_status", period)

        p = parameters(
            period
        ).gov.states.wv.tax.income.credits.low_income_family_tax_credit

        fpg = tax_unit("wv_low_income_family_tax_credit_fpg", period)

        # modified agi limit
        fpg_amount = p.fpg_percent[filing_status] * fpg
        income_threshold_total = p.income_threshold[filing_status] + fpg_amount
        return wv_agi <= income_threshold_total
