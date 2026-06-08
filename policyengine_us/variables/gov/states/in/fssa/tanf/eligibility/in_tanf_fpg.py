import numpy as np

from policyengine_us.model_api import *


class in_tanf_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF federal poverty guideline"
    unit = USD
    definition_period = MONTH
    reference = "https://www.in.gov/fssa/dfr/files/3000.pdf#page=5"
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states["in"].fssa.tanf.eligibility.fpg
        annual_fpg = p.first_person + p.additional_person * (size - 1)
        return np.ceil(annual_fpg / MONTHS_IN_YEAR)
