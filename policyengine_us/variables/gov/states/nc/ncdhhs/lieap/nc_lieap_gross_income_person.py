from policyengine_us.model_api import *


class nc_lieap_gross_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP gross income per person"
    defined_for = StateCode.NC
    reference = (
        # Section 300.09 (pages 10-13) and Section 300.10 (pages 15-17).
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        # Section 300.09 A takes the types of income to count from the FNS
        # manual, not its base periods or net-income deductions. The unearned
        # sources are listed for LIEAP itself, so a change to the federal SNAP
        # list does not change LIEAP income. Rental income, which LIEAP counts
        # as earned income, is in nc_lieap_earned_income only.
        unearned = max_(add(person, period, p.unearned_income_sources), 0)
        return person("nc_lieap_earned_income", period) + unearned
