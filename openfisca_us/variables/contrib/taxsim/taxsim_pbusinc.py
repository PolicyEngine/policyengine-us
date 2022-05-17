from openfisca_us.model_api import *


class taxsim_pbusinc(Variable):
    value_type = float
    entity = TaxUnit
    label = "QBI for the primary taxpayer (TAXSIM)"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        qbi = person("qualified_business_income", period)
        is_head = person("is_tax_unit_head", period)
        return tax_unit.sum(qbi * is_head)
