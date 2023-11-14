from policyengine_us.model_api import *


class vt_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child care and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=2"
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-151/section-5828c/"
        "https://www.irs.gov/pub/irs-prior/f2441--2022.pdf#page=1"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc
        # The form refers to 2022 Form 2441 line 11, which caps the credit at tax liability.
        federal_cdcc = tax_unit("capped_cdcc", period)
        return federal_cdcc * p.rate
