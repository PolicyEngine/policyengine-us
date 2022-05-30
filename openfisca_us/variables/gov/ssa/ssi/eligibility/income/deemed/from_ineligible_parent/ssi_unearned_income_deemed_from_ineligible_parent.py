from openfisca_us.model_api import *


class ssi_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

    def formula(person, period, parameters):
        eligible_child = person("is_ssi_aged_blind_disabled", period) & person("is_child", period)
        ineligible_parents_unearned_income = eligible_child * person.tax_unit.sum(
            person("ssi_unearned_income", period)
            * person("is_ssi_ineligible_parent", period)
        )