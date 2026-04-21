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
        # Avoid filing_status dependence (dependent_gross_income iterates over
        # gross-income sources and filing_status ultimately depends on
        # dependent_gross_income via head_of_household_eligible). Allocate the
        # tax-unit-level other_net_gain across head + spouse equally.
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = is_head | is_spouse
        num_head_or_spouse = tax_unit.sum(is_head_or_spouse)
        share = where(num_head_or_spouse > 0, 1 / num_head_or_spouse, 0)
        positive_other_net_gain = max_(0, tax_unit("other_net_gain", period))
        return is_head_or_spouse * positive_other_net_gain * share
