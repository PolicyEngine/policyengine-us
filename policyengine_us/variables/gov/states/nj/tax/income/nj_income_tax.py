from policyengine_us.model_api import *


class nj_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income
        agi = tax_unit("nj_agi", period)
        filing_status = tax_unit("filing_status", period)
        income_tax = tax_unit("nj_income_tax_before_refundable_credits", period)
        refundable_credits = tax_unit("nj_refundable_credits", period)
        # N.J.S.A. 54A:2-4 zeroes tax for filers at or below the filing
        # threshold; refundable credits then flow through against zero tax
        # rather than against the bracket-schedule amount.
        return where(
            agi <= p.filing_threshold[filing_status],
            -refundable_credits,
            income_tax - refundable_credits,
        )
