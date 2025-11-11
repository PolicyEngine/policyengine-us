from policyengine_us.model_api import *


class pa_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # All unearned income is countable (no deductions)
        return spm_unit.sum(person("tanf_gross_unearned_income", period))
