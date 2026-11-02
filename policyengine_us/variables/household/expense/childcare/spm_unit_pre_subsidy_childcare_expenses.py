from policyengine_us.model_api import *


class spm_unit_pre_subsidy_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit pre subsidy child care expenses"
    documentation = (
        "In a household calculation, the price of care before any subsidy. "
        "Datasets fill it from the ASEC's SPM_CHILDCAREXPNS, which holds what "
        "parents reported paying after any subsidy."
    )
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    unit = USD
