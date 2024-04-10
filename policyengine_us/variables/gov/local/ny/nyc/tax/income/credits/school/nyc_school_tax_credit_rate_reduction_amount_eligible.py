from policyengine_us.model_api import *


class nyc_school_tax_credit_rate_reduction_amount_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC School Tax Credit Rate Reduction Amount"
    definition_period = YEAR
    defined_for = "in_nyc"
    default_value = False

    def formula(tax_unit, period, parameters):
        # First get their NYC taxable income.
        nyc_taxable_income = tax_unit("nyc_taxable_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the School Tax Credit rate reduction amount part of the parameter tree.
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.school.rate_reduction

        # Get the tax unit's filing status.
        filing_status = tax_unit("filing_status", period)

        # Get the number of children in the tax unit.
        num_children = tax_unit("tax_unit_children", period)

        # Calulate eligibility.
        income_limit = p.income_limit[filing_status]
        income_eligible = nyc_taxable_income <= income_limit
        min_needed_children = p.min_children
        children_eligible = num_children >= min_needed_children

        return income_eligible * children_eligible
