from policyengine_us.model_api import *


class nyc_school_tax_credit_fixed_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC School Tax Credit Fixed Amount"
    unit = USD
    definition_period = YEAR
    defined_for = "nyc_school_tax_credit_fixed_amount_eligible"

    def formula(tax_unit, period, parameters):
        # Get the tax unit's filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the School Tax Credit fixed amount part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school.fixed

        # A joint return on which only one spouse qualifies gets that spouse's
        # individual amount (Form NYC-210 instructions).
        joint = filing_status == filing_status.possible_values.JOINT
        one_eligible_spouse = (
            tax_unit("head_spouse_count_not_dependent_elsewhere", period) == 1
        )
        return where(
            joint & one_eligible_spouse, p.amount.SINGLE, p.amount[filing_status]
        )
