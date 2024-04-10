from policyengine_us.model_api import *


class nyc_school_tax_credit_fixed_amount_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC School Tax Credit Fixed Amount"
    definition_period = YEAR
    defined_for = "in_nyc"
    default_value = False

    def formula(tax_unit, period, parameters):
        # Eligibility is based on having a federal AGI below $30k
        # and being an NYC full-time resident.

        # Get the NYC School Tax Credit Fixed Amount part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school.fixed

        # Get income that counts towards the NYC School Tax Credit.
        nyc_stc_income = tax_unit("nyc_school_credit_income", period)

        # Get the tax unit's filing status.
        filing_status = tax_unit("filing_status", period)

        # Get the number of children in the tax unit.
        num_children = tax_unit("tax_unit_children", period)

        # Calulate eligibility.
        income_limit = p.income_limit[filing_status]
        income_eligible = nyc_stc_income <= income_limit
        min_needed_children = p.min_children
        children_eligible = num_children >= min_needed_children
        
        return income_eligible * children_eligible
