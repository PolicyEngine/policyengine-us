from policyengine_us.model_api import *


class cbo_household_social_insurance_benefits(Variable):
    value_type = float
    entity = Household
    label = "CBO household social insurance benefits"
    documentation = (
        "Social insurance benefits included in CBO household income: Social "
        "Security, Medicare, unemployment insurance, and workers' compensation."
    )
    definition_period = YEAR
    unit = USD
    adds = "gov.household.cbo_social_insurance_benefits"
