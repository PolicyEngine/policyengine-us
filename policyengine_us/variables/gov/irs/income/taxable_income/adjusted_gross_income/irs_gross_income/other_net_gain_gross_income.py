from policyengine_us.model_api import *


class other_net_gain_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Allocated other net gain included in gross income"
    unit = USD
    documentation = "Positive Form 4797 other net gain allocated across primary tax-unit filers for gross-income calculations."
    definition_period = YEAR
    reference = "https://www.irs.gov/instructions/i461"

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        primary_filer = is_head | is_spouse
        primary_filer_count = max_(1, tax_unit.sum(primary_filer))
        share = 1 / primary_filer_count
        positive_other_net_gain = max_(0, tax_unit("other_net_gain", period))
        return primary_filer * positive_other_net_gain * share
