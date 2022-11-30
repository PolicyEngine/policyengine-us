from policyengine_us.model_api import *


class self_employment_tax_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employment tax ALD deduction"
    unit = USD
    documentation = "Above-the-line deduction for self-employment tax"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164#f"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        ald = person("self_employment_tax_ald_person", period)
        return tax_unit.sum(ald)
