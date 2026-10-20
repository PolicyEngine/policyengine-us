from policyengine_us.model_api import *


class ia_ssa_smme_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SMME countable income for Medicaid coverage group"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "SSI countable income plus any SSI payment. Deductions and financial groups of a Medicaid coverage category that differ from SSI are not modeled."
    reference = "https://hhs.iowa.gov/media/3987/download?inline=#page=77"

    def formula(person, period, parameters):
        return person("ssi_countable_income", period) + person("ssi", period)
