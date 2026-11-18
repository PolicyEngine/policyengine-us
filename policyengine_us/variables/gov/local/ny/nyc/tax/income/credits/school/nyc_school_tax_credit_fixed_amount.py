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

        # A joint return on which a spouse can be claimed as a dependent, so
        # that only the other spouse qualifies, gets that spouse's individual
        # amount (Form NYC-210 instructions).
        joint = filing_status == filing_status.possible_values.JOINT
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(joint & dependent_filer, p.amount.SINGLE, p.amount[filing_status])
