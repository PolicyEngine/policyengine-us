from policyengine_us.model_api import *


def create_adjust_income_limit_and_min_children_by_filing_status() -> Reform:
    class nyc_school_tax_credit_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for NYC School Tax Credit"
        definition_period = YEAR
        defined_for = "in_nyc"

        def formula(tax_unit, period, parameters):
            # Get the NYC School Tax Credit reform part of the parameter tree.
            p = parameters(period).gov.contrib.local.nyc.stc

            # Get income that counts towards the NYC School Tax Credit.
            nyc_stc_income = tax_unit("nyc_school_credit_income", period)

            # Get the tax unit's filing status.
            filing_status = tax_unit("filing_status", period)

            # Calculate eligibility.
            income_eligible = nyc_stc_income <= p.income_limit[filing_status]
            children_eligible = (
                tax_unit("tax_unit_children", period) >= p.min_children
            )

            return income_eligible & children_eligible

    class nyc_school_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "NYC School Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = "nyc_school_tax_credit_eligible"

        adds = [
            "nyc_school_tax_credit_fixed_amount",
            "nyc_school_tax_credit_rate_reduction_amount",
        ]

    class reform(Reform):
        def apply(self):
            self.update_variable(nyc_school_tax_credit_eligible)
            self.update_variable(nyc_school_tax_credit)

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
