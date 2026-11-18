from policyengine_us.model_api import *


class nd_ccap_workforce_benefit_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "North Dakota CCAP family meets the Workforce Benefit employment test"
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_20_40.htm"

    def formula_2024_06_01(spm_unit, period, parameters):
        # North Dakota requires at least one caretaker in qualifying child care
        # employment (400-28-20-40); the model treats the tax unit head and
        # spouse as the caretakers, as the activity test does.
        person = spm_unit.members
        caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        qualifies = person("nd_ccap_workforce_benefit_eligible_parent", period)
        return spm_unit.any(caretaker & qualifies)
