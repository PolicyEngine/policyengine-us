from policyengine_us.model_api import *


class vt_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont low-income child care and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2"
        "https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5828c/"
    )
    defined_for = "vt_low_income_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc.low_income
        federal_cdcc = tax_unit("capped_cdcc", period)
        return p.rate * federal_cdcc
