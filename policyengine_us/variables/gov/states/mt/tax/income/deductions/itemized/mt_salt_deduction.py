from policyengine_us.model_api import *


class mt_salt_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana state and local tax deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7"
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/"
        # Montana Code Annotated MT Code § 15-30-2131 (2022) (1)(a)
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # Not included the SALT tax, only real estate taxes
        p = parameters(period).gov.irs.deductions
        filing_status = person.tax_unit("filing_status", period)
        real_estate_tax = person("real_estate_taxes", period)
        return min_(
            real_estate_tax,
            p.itemized.salt_and_real_estate.cap[filing_status],
        )
