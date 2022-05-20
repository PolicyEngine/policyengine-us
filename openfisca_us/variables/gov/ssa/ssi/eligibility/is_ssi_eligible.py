from openfisca_us.model_api import *


class ssi_eligible_people(Variable):
    value_type = int
    entity = MaritalUnit
    definition_period = YEAR
    label = "Eligible people for Supplemental Security Income"

    def formula(marital_unit, period, parameters):
        abds = add(marital_unit, period, ["is_ssi_aged_blind_disabled"])
        meets_resource_test = marital_unit("meets_ssi_resource_test")
        return meets_resource_test * abds
