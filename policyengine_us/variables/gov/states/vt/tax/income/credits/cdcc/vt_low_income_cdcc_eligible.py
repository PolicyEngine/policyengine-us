from policyengine_us.model_api import *


class vt_low_income_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Vermont low-income child care and dependent care credit"
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2"
        "https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5828c/"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc.low_income
        filing_status = tax_unit("filing_status", period)
        federal_agi_threshold = p.income_threshold[filing_status]
        federal_agi = tax_unit("adjusted_gross_income", period)
        # Law says "less than" but tax form says "$x or less". We apply form rules.
        return federal_agi <= federal_agi_threshold
