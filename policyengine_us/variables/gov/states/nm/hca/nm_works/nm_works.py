from policyengine_us.model_api import *


class nm_works(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0620.html",
        "https://www.hca.nm.gov/lookingforassistance/temporary_assistance_for_needy_families/",
    )
    defined_for = "nm_works_eligible"

    def formula(spm_unit, period, parameters):
        # Per 8.102.620 NMAC:
        # Benefit = Payment Standard - Net Countable Income
        maximum_benefit = spm_unit("nm_works_maximum_benefit", period)
        countable_income = spm_unit("nm_works_countable_income", period)
        return max_(maximum_benefit - countable_income, 0)
