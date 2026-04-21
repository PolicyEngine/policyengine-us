from policyengine_us.model_api import *


class pa_uc_dependent_children_count(Variable):
    value_type = int
    entity = Person
    label = "Pennsylvania unemployment compensation dependent children count"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=159",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # § 404(e)(3): a dependent child is any child or stepchild of the
        # claimant "wholly or chiefly supported" by the claimant and under
        # eighteen years of age (older if unable to work due to infirmity,
        # which is not modeled here). Attribute the tax-unit count of
        # qualifying children only to the claimant (head of the tax unit)
        # to avoid double-counting if multiple adults file UC claims.
        tax_unit = person.tax_unit
        dep_age = tax_unit.members("age", period.this_year)
        is_dep = tax_unit.members("is_tax_unit_dependent", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        qualifies = is_dep & (dep_age < p.dependent_allowance.child_age_limit)
        count_in_tax_unit = tax_unit.sum(qualifies)
        is_head = person("is_tax_unit_head", period)
        return where(is_head, count_in_tax_unit, 0)
