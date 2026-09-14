from policyengine_us.model_api import *


class spm_unit_ordinary_housing_subsidy_reported(Variable):
    value_type = float
    default_value = -1
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Source-supported ordinary housing subsidy value outside SPM scope"
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14"

    def formula(spm_unit, period, parameters):
        # Each year requires its own source declaration. A formula prevents the
        # generic USD-input uprating rule from manufacturing a later report.
        return -1
