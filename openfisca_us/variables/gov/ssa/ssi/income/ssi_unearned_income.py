from openfisca_us.model_api import *


class ssi_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income unearned income"
    label = "SSI unearned income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/1382a#a_2"

    def formula(person, period, parameters):
        sources = parameters(period).ssa.ssi.income.sources.unearned
        return add(person, period, sources)
