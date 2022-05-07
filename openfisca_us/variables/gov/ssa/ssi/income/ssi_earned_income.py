from openfisca_us.model_api import *


class ssi_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income earned income"
    label = "SSI earned income"
    unit = USD

    def formula(person, period, parameters):
        sources = parameters(period).ssa.ssi.income.sources.earned
        return add(person, period, sources)
