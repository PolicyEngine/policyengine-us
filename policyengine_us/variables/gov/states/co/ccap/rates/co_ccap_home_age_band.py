from policyengine_us.model_api import *


class COCCAPHomeAgeBand(Enum):
    MONTHS_0_TO_24 = "0 to 24 months"
    MONTHS_24_TO_YEARS_6 = "24 months to 6 years"
    SCHOOL_AGE = "School age"


class co_ccap_home_age_band(Variable):
    value_type = Enum
    entity = Person
    possible_values = COCCAPHomeAgeBand
    default_value = COCCAPHomeAgeBand.MONTHS_0_TO_24
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program licensed home rate age band"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(A), PDF page 119.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
        "https://drive.google.com/file/d/1wK5dCjkW_uqj06tTd0af9-fC6gAfGu5v/view",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap.rates.age_band
        age_in_months = person("monthly_age", period) * MONTHS_IN_YEAR
        return select(
            [
                age_in_months < p.home_months_24_to_years_6_minimum,
                age_in_months < p.school_age_minimum,
            ],
            [
                COCCAPHomeAgeBand.MONTHS_0_TO_24,
                COCCAPHomeAgeBand.MONTHS_24_TO_YEARS_6,
            ],
            default=COCCAPHomeAgeBand.SCHOOL_AGE,
        )
