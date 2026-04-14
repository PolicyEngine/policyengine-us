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
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        share = where(joint, 0.5, 1.0)
        positive_other_net_gain = max_(0, tax_unit("other_net_gain", period))
        return (is_head | is_spouse) * positive_other_net_gain * share
