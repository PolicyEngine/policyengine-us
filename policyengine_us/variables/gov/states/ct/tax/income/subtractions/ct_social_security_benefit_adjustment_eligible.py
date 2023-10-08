from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut social security benefit adjustment"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.social_security
        filing_status = tax_unit("filing_status", period)
        agi = add(tax_unit, period, ["adjusted_gross_income"])
        income_threshold = p.income_threshold[filing_status]
        return agi < income_threshold
