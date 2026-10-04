from policyengine_us.model_api import *


class ia_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP annual income limit"
    documentation = (
        "200 percent of the household's federal poverty guideline, with no "
        "rounding: $31,300 for one person plus $11,000 for each additional "
        "member in FY26."
    )
    reference = (
        # Section 5.10 (page 18) and Appendix B (page 89).
        "https://hhs.iowa.gov/media/17262/download?inline#page=89",
        # Section 2.1 note: the threshold is 200% FPG; 150.00% is a form
        # artifact.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=9",
        "https://hhs.iowa.gov/programs/programs-and-services/liheap",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.eligibility
        return p.fpg_rate * spm_unit("ia_liheap_fpg", period)
