from policyengine_us.model_api import *


class medicaid_optional_senior_or_disabled_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Countable income for Medicaid's optional senior or disabled pathway"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.kff.org/medicaid/medicaid-financial-eligibility-for-seniors-and-people-with-disabilities-findings-from-a-50-state-survey/",
        # Missouri MHABD budgeting order and rounding
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-25/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-40/",
    )

    def formula(person, period, parameters):
        # Aggregate monthly budgets while retaining the annual input contract.
        return person(
            "medicaid_optional_senior_or_disabled_countable_income_monthly", period
        )
