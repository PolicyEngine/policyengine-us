from policyengine_us.model_api import *


class ar_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Arkansas gross income for each individual"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/arkansas-code-of-1987/title-26-taxation/subtitle-5-state-taxes/chapter-51-income-taxes/subchapter-4-computation-of-tax-liability/section-26-51-404-gross-income-generally"
    defined_for = StateCode.AR

    adds = "gov.states.ar.tax.income.gross_income_sources"
