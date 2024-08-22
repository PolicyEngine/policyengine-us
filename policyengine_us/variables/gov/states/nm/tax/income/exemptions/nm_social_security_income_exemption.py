from policyengine_us.model_api import *


class nm_social_security_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico social security income exemption"
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # This is the amount of Social Security included in AGI.
        social_security_income = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.social_security_income
        agi = tax_unit("adjusted_gross_income", period)
        income_limit = agi <= p.income_limit[filing_status]
        return where(income_limit, social_security_income, 0)
