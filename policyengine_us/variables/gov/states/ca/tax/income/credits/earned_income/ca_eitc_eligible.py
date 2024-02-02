from policyengine_us.model_api import *


class ca_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "CalEITC eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members

        ca_eitc_eligible_person = person("ca_eitc_eligible_person", period)

        return tax_unit.any(ca_eitc_eligible_person)
