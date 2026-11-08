from policyengine_us.model_api import *


class COCCAPQualifiedExemptAgeBand(Enum):
    UNDER_5 = "Under 5 years"
    AGE_5_AND_OVER = "5 years and over"


class co_ccap_qualified_exempt_age_band(Variable):
    value_type = Enum
    entity = Person
    possible_values = COCCAPQualifiedExemptAgeBand
    default_value = COCCAPQualifiedExemptAgeBand.UNDER_5
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program qualified exempt rate age band"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(A), PDF page 119.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
        # County rate plans, Provider Type (Exempt): Regular <5 Years, >5 Years.
        "https://drive.google.com/drive/folders/1YSLL5Sn32NyKbp8Z0063ldFbAhQwfHW_",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap.rates.age_band
        age_in_months = person("monthly_age", period) * MONTHS_IN_YEAR
        return where(
            age_in_months < p.qualified_exempt_age_5_and_over_minimum,
            COCCAPQualifiedExemptAgeBand.UNDER_5,
            COCCAPQualifiedExemptAgeBand.AGE_5_AND_OVER,
        )
