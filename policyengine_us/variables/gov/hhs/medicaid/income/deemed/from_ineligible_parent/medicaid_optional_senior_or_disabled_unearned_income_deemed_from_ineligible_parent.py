from policyengine_us.model_api import *


class medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled unearned income deemed from ineligible parent"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1165",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/",
    )

    def formula(person, period, parameters):
        # Aggregate monthly budgets while retaining the annual input contract.
        return person(
            "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent_monthly",
            period,
        )
