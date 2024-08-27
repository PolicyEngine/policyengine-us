from policyengine_us.model_api import *


class az_fpg_rate(Variable):
    value_type = float
    entity = Person
    label = "Needy family Federal Poverty Guideline Percentage Limit"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        # Determine whether the head-of-household is a non-parent relative
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.rate
        tax_unit_head = person("is_tax_unit_head", period)
        parent = person("is_parent_of_filer_or_spouse", period)
        return where(tax_unit_head * parent, p.base, p.non_parent)
