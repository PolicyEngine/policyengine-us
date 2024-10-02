from policyengine_us.model_api import *


class vt_charitable_contribution_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont charitable contribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-151/section-5822/"
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf#page=1"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        charitable_contributions = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        p = parameters(period).gov.states.vt.tax.income.credits
        return p.charitable.calc(charitable_contributions)
