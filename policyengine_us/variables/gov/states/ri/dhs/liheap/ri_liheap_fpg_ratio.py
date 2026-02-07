from policyengine_us.model_api import *


class ri_liheap_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island LIHEAP federal poverty guideline ratio"
    definition_period = YEAR
    defined_for = StateCode.RI
    unit = "/1"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program",
    )

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        fpg = spm_unit("spm_unit_fpg", period)
        return income / fpg
