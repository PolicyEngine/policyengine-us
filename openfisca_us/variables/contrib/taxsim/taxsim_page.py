from policyengine_us.model_api import *


class taxsim_page(Variable):
    value_type = int
    entity = TaxUnit
    label = "Age of primary taxpayer"
    unit = "year"
    documentation = "Age of primary taxpayer December 31st of the tax year (or zero). Taxpayer and spouse age variables determine eligibility for additional standard deductions, personal exemption, EITC and AMT exclusions."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        age = person("age", period)
        return tax_unit.sum(age * is_head)
