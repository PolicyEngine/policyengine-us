from openfisca_us.model_api import *


class tanf_total_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF gross income"
    documentation = "Gross income for calculating Temporary Assistance for Needy Families benefit. Includes both gross earned and unearned income."
    unit = USD
    reference = "https://www.dhs.state.il.us/page.aspx?item=15814"
