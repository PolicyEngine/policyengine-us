from policyengine_us.model_api import *


class va_eitc_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia Earned Income Tax Credit per individual when married filing seperately"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        refundable_eitc = person.tax_unit("va_refundable_eitc", period)
        non_refundable_eitc = person.tax_unit("va_non_refundable_eitc", period)
        claims_refundable = person.tax_unit(
            "va_claims_refundable_eitc", period
        )
        va_agi_share = person("va_agi_share", period)
        eitc_claimed = where(
            claims_refundable, refundable_eitc, non_refundable_eitc
        )
        return eitc_claimed * va_agi_share
