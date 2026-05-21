from policyengine_us.model_api import *


class medicaid_work_income_threshold(Variable):
    value_type = float
    entity = Person
    label = "The monthly income threshold for a person to demonstrate Community Engagement (CE) for Medicaid"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters) -> float:
        p = parameters(period).gov
        federal_min_wage: float = p.dol.minimum_wage
        hours: int = p.hhs.medicaid.eligibility.work_requirements.monthly_hours_threshold

        return federal_min_wage * hours

