from policyengine_us.model_api import *


class ia_ssa_smme_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SMME countable income for Medicaid coverage group"
    definition_period = MONTH
    unit = USD
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    documentation = "Override with income calculated using the deductions and financial group of the actual Medicaid coverage category when these differ from SSI."

    def formula(person, period, parameters):
        return person("ssi_countable_income", period) + person("ssi", period)
