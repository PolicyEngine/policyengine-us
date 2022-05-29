from openfisca_us.model_api import *


class ssi_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        earned_income = person("ssi_earned_income_deemed_from_ineligible_spouse", period)
        unearned_income = person("ssi_unearned_income_deemed_from_ineligible_spouse", period)
        income = earned_income + unearned_income
        ssi = parameters(period).ssa.ssi.amount
        person_amount = (ssi.couple - ssi.individual) * MONTHS_IN_YEAR
        return where(income > person_amount, income, 0)