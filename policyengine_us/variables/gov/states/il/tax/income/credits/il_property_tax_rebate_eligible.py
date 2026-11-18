from policyengine_us.model_api import *


class il_property_tax_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Illinois property tax rebate"
    documentation = (
        "Eligibility for Illinois's one-time property tax rebate paid in 2022 and "
        "determined from the 2021 return. PolicyEngine attributes the payment to "
        "eligibility tax year 2021. A true eligibility indicator in another year does "
        "not establish inclusion in that year's refundable-credit total."
    )
    defined_for = StateCode.IL
    definition_period = YEAR
    reference = "https://www.illinois.gov/news/release.html?releaseid=25425"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.property_tax_rebate
        federal_agi = tax_unit("adjusted_gross_income", period)
        joint = tax_unit("tax_unit_is_joint", period)
        income_limit = where(joint, p.income_limit.joint, p.income_limit.other)
        return federal_agi <= income_limit
