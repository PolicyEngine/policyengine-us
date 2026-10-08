from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ga_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP annual income limit"
    defined_for = StateCode.GA
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/GA_BenefitMatrix_Heat-Cool_2026.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap.eligibility
        size = spm_unit("ga_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        size_share = smi(size, state, period, parameters) / four_person_smi
        # Flooring 60% of the four-person SMI before applying the federal size
        # factor reproduces all 16 FY2026 published limits. This is a numerical
        # reconciliation; the sources do not expressly specify the floor order.
        four_person_limit = np.floor(four_person_smi * p.smi_rate)
        return where(size > 0, np.floor(four_person_limit * size_share), 0)
