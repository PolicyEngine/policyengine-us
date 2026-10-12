from policyengine_us.model_api import *


class ks_liheap_household_size_group(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP household size group"
    documentation = "Benefit matrix household size group: 1 for households of one to four countable members, 2 for five or more."
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf#page=1"
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.payment
        size = spm_unit("ks_liheap_household_size", period)
        return p.household_size_group.calc(size)
