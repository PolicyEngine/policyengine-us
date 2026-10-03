from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class fl_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Florida LIHEAP annual heating income limit"
    defined_for = StateCode.FL
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/FL_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://liheapch.acf.gov/delivery/income_eligibility.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.eligibility
        size = spm_unit("fl_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        size_share = smi(size, state, period, parameters) / four_person_smi
        # This floor order reconciles all FY2026 matrix rows for sizes 1-12;
        # the sources do not expressly prescribe the rounding order.
        four_person_limit = np.floor(four_person_smi * p.smi_rate)
        # The printed size-13 maximum, $157,686, equals 100% of SMI. Follow
        # the matrix's explicit 60% rule instead ($94,610). The federal table
        # restricts its 150%-FPG large-household exception to cooling/crisis.
        # Larger sizes follow the federal factors without table verification.
        return where(size > 0, np.floor(four_person_limit * size_share), 0)
