from policyengine_us.model_api import *


class in_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/files/2800.pdf",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Get gross unearned income from federal baseline
        # No disregard for unearned income in benefit calculation
        # Per Policy Manual Chapter 2800
        return spm_unit("tanf_gross_unearned_income", period)
