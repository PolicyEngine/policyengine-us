from policyengine_us.model_api import *


class nc_lieap_gross_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP gross income per person"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,11,12,13,15,16,17"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.income.sources
        # Section 300.09 incorporates FNS income types, not its base periods or
        # net-income deductions. Rental income is already in LIEAP earned income.
        sources = [source for source in p.unearned if source != "rental_income"]
        return person("nc_lieap_earned_income", period) + max_(
            add(person, period, sources), 0
        )
