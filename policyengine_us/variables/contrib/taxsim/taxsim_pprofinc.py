from policyengine_us.model_api import *


class taxsim_pprofinc(Variable):
    value_type = float
    entity = TaxUnit
    label = "SSTB income of the primary and secondary taxpayer (TAXSIM)"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        sstb = person("sstb_self_employment_income", period)
        return tax_unit.sum(sstb * is_head_or_spouse)
