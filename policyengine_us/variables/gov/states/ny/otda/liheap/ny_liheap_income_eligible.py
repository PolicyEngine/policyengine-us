from policyengine_us.model_api import *


class ny_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New York State LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/programs/heap/",
        "https://liheapch.acf.gov/tables/liheap/FY2025SMI/FY25smi.htm",
    )
    documentation = "Uses 60% of State Median Income as income limit per federal LIHEAP regulations"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        state_median_income = spm_unit("hhs_smi", period)
        # The income concept is not clearly defined, assuming IRS gross income
        income = add(spm_unit, period, ["irs_gross_income"])
        smi_limit = state_median_income * p.smi_limit
        
        # Check categorical eligibility through other programs
        receives_snap = spm_unit("snap", period) > 0
        receives_tanf = spm_unit("tanf", period) > 0
        person = spm_unit.members
        receives_ssi = spm_unit.sum(person("ssi", period)) > 0
        
        return (income <= smi_limit) | receives_snap | receives_tanf | receives_ssi
