from policyengine_us.model_api import *


class tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF gross earned income"
    documentation = "Gross earned income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD
    reference = "https://www.dhs.state.il.us/page.aspx?item=15814"
    adds = "gov.hhs.tanf.cash.income.gross.sources.earned"
