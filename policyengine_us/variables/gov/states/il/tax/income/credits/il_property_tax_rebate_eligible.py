from policyengine_us.model_api import *


class il_property_tax_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Illinois property tax rebate"
    defined_for = StateCode.IL
    definition_period = YEAR
    reference = "https://www.illinois.gov/news/release.html?releaseid=25425"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.property_tax_rebate
        federal_agi = tax_unit("adjusted_gross_income", period)
        joint = tax_unit("tax_unit_is_joint", period)
        income_limit = where(joint, p.income_limit.joint, p.income_limit.other)
        return federal_agi <= income_limit
