from policyengine_us.model_api import *


class id_eligible_military_retirement_income(Variable):
    value_type = float
    entity = Person
    label = "Idaho eligible military retirement and survivor income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://legislature.idaho.gov/wp-content/uploads/sessioninfo/2025/legislation/H0479.pdf",
    )

    def formula(person, period, parameters):
        # Section 63-3022A covers the retired member and the member's
        # unremarried widow or widower, including under the 2025 amendment.
        surviving_spouse = person("is_surviving_spouse", period)
        # Marital units contain one unmarried person or a married couple,
        # independently of other relatives and of how spouses file taxes.
        married = person.marital_unit.nb_persons() > 1
        eligible_survivor = surviving_spouse & ~married
        retirement_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        return retirement_pay + survivor_pay * eligible_survivor
