from policyengine_us.model_api import *


def create_adjust_income_limit_and_min_children_by_filing_status() -> Reform:
    class nyc_school_tax_credit_fixed_amount_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for NYC School Tax Credit Fixed Amount"
        definition_period = YEAR
        defined_for = "in_nyc"

        def formula(tax_unit, period, parameters):
            # Eligibility is based on having a federal AGI below $30k
            # and being an NYC full-time resident.

            # Get the NYC School Tax Credit Fixed Amount reform part of the parameter tree.
            p = parameters(period).gov.contrib.local.nyc.stc.fixed

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

    class nyc_school_tax_credit_rate_reduction_amount_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for NYC School Tax Credit Rate Reduction Amount"
        definition_period = YEAR
        defined_for = "in_nyc"

        def formula(tax_unit, period, parameters):
            # First get their NYC taxable income.
            nyc_taxable_income = tax_unit("nyc_taxable_income", period)

            # Then get their filing status.
            filing_status = tax_unit("filing_status", period)

            # Then get the School Tax Credit rate reduction reform part of the parameter tree.
            p = parameters(period).gov.contrib.local.nyc.stc.rate_reduction

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

    class reform(Reform):
        def apply(self):
            self.update_variable(nyc_school_tax_credit_fixed_amount_eligible)
            self.update_variable(
                nyc_school_tax_credit_rate_reduction_amount_eligible
            )

    return reform


def create_adjust_income_limit_by_filing_status_and_eligibility_by_children_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_adjust_income_limit_and_min_children_by_filing_status()

    p = parameters(period).gov.contrib.local.nyc.stc

    if p.adjust_income_limit_by_filing_status_and_eligibility_by_children:
        return create_adjust_income_limit_and_min_children_by_filing_status()
    else:
        return None


adjust_income_limit_and_min_children_by_filing_status = create_adjust_income_limit_by_filing_status_and_eligibility_by_children_reform(
    None, None, bypass=True
)
