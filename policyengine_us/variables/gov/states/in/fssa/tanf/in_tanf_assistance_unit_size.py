from policyengine_us.model_api import *


class in_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Indiana TANF assistance unit size"
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Indiana TANF assistance group includes persons whose income, resources,
        # or needs are considered in determining eligibility and benefit amount
        # Per IC 12-14-1-0.5
        return spm_unit("spm_unit_size", period)
