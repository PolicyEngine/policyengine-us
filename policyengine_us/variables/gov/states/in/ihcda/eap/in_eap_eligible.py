from policyengine_us.model_api import *


class in_eap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Indiana EAP household eligibility"
    defined_for = StateCode.IN
    reference = "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=23,29,69,70,73,74,75"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].ihcda.eap
        income = spm_unit("in_eap_income", period)
        limit = np.floor(spm_unit("in_eap_smi", period) * p.income_limit)
        # Section 4.4 permits an ineligible adult to apply for eligible household members.
        # Emancipated minors, residency duration, eviction writs, SSNs, and sanctions
        # cannot be determined here. Section 8.8 separates household eligibility from
        # whether each utility can receive a benefit; burden is checked in in_eap.
        return (
            spm_unit.any(spm_unit.members("is_citizen_or_legal_immigrant", period))
            & spm_unit.any(spm_unit.members("age", period) >= p.adult_age)
            & (income <= limit)
        )
