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
        p = parameters(period).gov.usda.snap.income.sources
        earned_sources = parameters(
            period
        ).gov.states.nc.ncdhhs.lieap.earned_income_sources
        # Section 300.09 incorporates FNS income types, not its base periods or
        # net-income deductions. A SNAP unearned source that LIEAP counts as
        # earned income (rental income) is already in nc_lieap_earned_income.
        sources = [source for source in p.unearned if source not in earned_sources]
        return person("nc_lieap_earned_income", period) + max_(
            add(person, period, sources), 0
        )
