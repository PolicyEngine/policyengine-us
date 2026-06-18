import numpy as np

from policyengine_us.model_api import *


class in_tanf_initial_gross_income_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF initial applicant gross income standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-1-1.7",
        "https://www.in.gov/fssa/dfr/files/3000.pdf#page=4",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.eligibility
        fpg = spm_unit("in_tanf_fpg", period)
        return np.ceil(fpg * p.initial.gross_income.fpg_rate)
