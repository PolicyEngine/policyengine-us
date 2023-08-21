from policyengine_us.model_api import *


class nj_property_tax_deduction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey property tax deduction eligibility"
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income

        filing_status = tax_unit("filing_status", period)
        nj_agi = tax_unit("nj_agi", period)
        income_eligible = nj_agi > p.filing_threshold[filing_status]

        pays_ptax = add(tax_unit, period, ["real_estate_taxes"]) > 0
        pays_rent = tax_unit("rents", period)

        return income_eligible & (pays_ptax | pays_rent)
