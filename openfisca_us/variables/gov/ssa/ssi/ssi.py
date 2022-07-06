from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    label = "Supplemental Security Income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382"

    def formula(person, period, parameters):
<<<<<<< HEAD
        marital_unit = person.marital_unit
        ssi_eligible_people = marital_unit("ssi_eligible_people", period)
        marital_unit_ssi = marital_unit("marital_unit_ssi", period)
        return where(
            ssi_eligible_people > 0, marital_unit_ssi / ssi_eligible_people, 0
        )
=======
        return max_(0, person("uncapped_ssi", period))
>>>>>>> f909fcb9f2caa11ac0da2eccd9a37fdbbfaba246
