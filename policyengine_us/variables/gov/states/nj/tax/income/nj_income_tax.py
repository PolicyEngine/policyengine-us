from policyengine_us.model_api import *


class nj_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get the NJ tax portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income

        # Get NJ AGI.
        agi = tax_unit("nj_agi", period)

        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Get the refundable credits and the income tax before refundable credits.
        income_tax = tax_unit(
            "nj_income_tax_before_refundable_credits", period
        )
        refundable_credits = tax_unit("nj_refundable_credits", period)

        # If taxable income is below the filing threshold, the tax should not be positive.
        # Tax could still be negative if filer is due refundable credits.
        return where(
            agi < p.filing_threshold[filing_status],
            min_(0, income_tax - refundable_credits),
            income_tax - refundable_credits,
        )
