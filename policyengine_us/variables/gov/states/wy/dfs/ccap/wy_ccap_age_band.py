from policyengine_us.model_api import *


class WYCCAPAgeBand(Enum):
    AGE_0_TO_11_MONTHS = "0 to 11 months"
    AGE_12_TO_23_MONTHS = "12 to 23 months"
    AGE_2_TO_3_YEARS = "2 to 3 years"
    AGE_4_TO_5_YEARS = "4 to 5 years"
    AGE_6_TO_13_YEARS = "6 to 13 years"


class wy_ccap_age_band(Variable):
    value_type = Enum
    entity = Person
    possible_values = WYCCAPAgeBand
    default_value = WYCCAPAgeBand.AGE_2_TO_3_YEARS
    definition_period = MONTH
    defined_for = StateCode.WY
    label = "Wyoming CCAP child age band"
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §9(o), eff. 05/07/2025 (PDF p. 25)
        "https://dfs.wyo.gov/services/family-services/child-care/",  # Wyoming DFS Table I - Child Care Sliding Fee Scale, eff. 04/01/25-03/31/26 (single page)
    )

    def formula(person, period, parameters):
        # Rules Ch. 1 §9(o): rates are based on the child's age on the first
        # day of the month; the age in whole years approximates that date.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.wy.dfs.ccap.age_group
        return p.months.calc(age_in_months)
