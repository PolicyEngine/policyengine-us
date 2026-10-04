from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ia_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP federal poverty guideline"
    documentation = (
        "Annual 100 percent federal poverty guideline for the Iowa LIHEAP "
        "household size, from the guideline year the program adopts for the "
        "season. The FY26 Appendix B table equals 200 percent of the 2025 "
        "guideline, so model period 2026 reads the guideline one year back. "
        "Zero when no member counts toward household size."
    )
    reference = (
        # Appendix B, Poverty Guidelines (page 89).
        "https://hhs.iowa.gov/media/17262/download?inline#page=89",
        "https://hhs.iowa.gov/programs/programs-and-services/liheap",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.eligibility
        size = spm_unit("ia_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        return where(size > 0, guideline, 0)
