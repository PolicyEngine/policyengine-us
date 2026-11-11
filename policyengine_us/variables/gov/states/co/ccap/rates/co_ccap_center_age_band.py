from policyengine_us.model_api import *


class COCCAPCenterAgeBand(Enum):
    MONTHS_0_TO_18 = "0 to 18 months"
    MONTHS_18_TO_36 = "18 to 36 months"
    MONTHS_36_TO_YEARS_6 = "36 months to 6 years"
    SCHOOL_AGE = "School age"


class co_ccap_center_age_band(Variable):
    value_type = Enum
    entity = Person
    possible_values = COCCAPCenterAgeBand
    default_value = COCCAPCenterAgeBand.MONTHS_0_TO_18
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program licensed center rate age band"
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
                age_in_months < p.center_months_18_to_36_minimum,
                age_in_months < p.center_months_36_to_years_6_minimum,
                age_in_months < p.school_age_minimum,
            ],
            [
                COCCAPCenterAgeBand.MONTHS_0_TO_18,
                COCCAPCenterAgeBand.MONTHS_18_TO_36,
                COCCAPCenterAgeBand.MONTHS_36_TO_YEARS_6,
            ],
            default=COCCAPCenterAgeBand.SCHOOL_AGE,
        )
