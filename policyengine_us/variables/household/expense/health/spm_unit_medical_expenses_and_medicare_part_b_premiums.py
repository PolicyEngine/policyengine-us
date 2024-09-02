from policyengine_us.model_api import *


class spm_unit_medical_expenses_and_medicare_part_b_premiums(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit medical expenses including Medicare Part B premiums"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
