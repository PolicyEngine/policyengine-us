from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ri_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP annual income limit"
    defined_for = StateCode.RI
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        # DHS FY2027 sheet, linked by the administering provider EBCAP.
        "https://9e947cb6.delivery.rocketcdn.me/wp-content/uploads/2026/09/LIHEAP-Income-Eligibilty-FFY-2027.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.eligibility
        size = spm_unit("ri_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        size_share = smi(size, state, period, parameters) / four_person_smi
        # The FY2026/FY2027 tables floor 60% of the four-person amount before
        # adjusting for size, then floor again. This matches all 14 rows;
        # the ordering is a numerical reconciliation, not explicit legal text.
        four_person_limit = np.floor(four_person_smi * p.smi_rate)
        return where(size > 0, np.floor(four_person_limit * size_share), 0)
