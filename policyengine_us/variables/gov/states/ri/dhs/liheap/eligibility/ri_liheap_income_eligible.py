from policyengine_us.model_api import *


class ri_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Rhode Island LIHEAP income eligibility"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        income = add(spm_unit, period, ["irs_gross_income"])
        income_limit = spm_unit("hhs_smi", period) * p.smi_limit
        return income <= income_limit
