from openfisca_us.model_api import *


class ssi_unearned_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income deemed from spouse"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_ssi_aged_blind_disabled", period)
        unearned_income = person("ssi_personal_unearned_income", period)
        should_deem_spousal_income = person.marital_unit(
            "ssi_deeming_occurs", period
        )
        spousal_deemed_income = person.marital_unit.sum(
            ~eligible * unearned_income
        )
        return eligible * should_deem_spousal_income * spousal_deemed_income
