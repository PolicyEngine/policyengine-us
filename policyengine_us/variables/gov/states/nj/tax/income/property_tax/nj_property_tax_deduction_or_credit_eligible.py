from policyengine_us.model_api import *


class nj_property_tax_deduction_or_credit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax deduction/credit eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Don't forget to divide the threshold if filing separately? They have to also live together.

        # Get the NJ tax portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income

        # First check income-eligibliy, defined as NJ AGI > threshold based on filing status.
        filing_status = tax_unit("filing_status", period)
        nj_agi = tax_unit("nj_agi", period)
        income_eligible = nj_agi > p.filing_threshold[filing_status]

        # Next check if they paid property taxes (either directly or through rent).
        direct_property_taxes = tax_unit("nj_homeowners_property_tax", period)
        rent = tax_unit("rent", period)
        paid_property_taxes = (direct_property_taxes + rent) > 0

        return income_eligible * paid_property_taxes
