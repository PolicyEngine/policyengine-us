from policyengine_us.model_api import *


class ia_reportable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa reportable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=11"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=10"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        benefits = add(tax_unit, period, ["social_security"])
        income = (
            tax_unit("adjusted_gross_income", period)
            - add(tax_unit, period, ["taxable_social_security"])
            + add(tax_unit, period, ["tax_exempt_interest_income"])
        )
        p = parameters(period).gov.states.ia.tax.income
        filing_status = tax_unit("filing_status", period)
        deduction = p.reportable_social_security.deduction[filing_status]
        return p.reportable_social_security.fraction * min_(
            benefits, max_(0, income - deduction)
        )
