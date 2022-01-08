from openfisca_us.model_api import *


class tanf_total_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF gross income"
    documentation = "Gross income for calculating Temporary Assistance for Needy Families benefit. Includes both gross earned and unearned income."
    unit = USD
    reference = "https://www.dhs.state.il.us/page.aspx?item=15814"

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("market_income", period))
