from policyengine_us.model_api import *


class medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled income deemed from ineligible spouse"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-05/",
    )
    defined_for = "is_ssi_eligible_individual"
    unit = USD

    def formula(person, period, parameters):
        # Aggregate monthly budgets while retaining the annual input contract.
        return person(
            "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse_monthly",
            period,
        )
