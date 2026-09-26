from policyengine_us.model_api import *


class ar_gross_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas gross income when married filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/arkansas/title-26/subtitle-5/chapter-51/subchapter-4/section-26-51-404/"
    defined_for = StateCode.AR

    adds = "gov.states.ar.tax.income.gross_income.sources.individual"
