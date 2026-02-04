from policyengine_us.model_api import *


class ri_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island LIHEAP benefit"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program",
    )

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("ri_liheap_eligible", period)
        heating_benefit = spm_unit("ri_liheap_heating_benefit", period)
        return where(eligible, heating_benefit, 0)
