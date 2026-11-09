from policyengine_us.model_api import *


class nj_employer_temporary_disability_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employer temporary disability insurance contribution"
    documentation = (
        "Employer contribution to the New Jersey State disability benefits fund "
        "at the new-employer rate, on wages up to the unemployment insurance "
        "taxable wage base. Employers with an approved private disability plan "
        "do not pay it; the model assumes coverage under the State plan."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/labor/ea/employer-services/rate-info/",
        "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf#page=65",
    )

    def formula(person, period, parameters):
        rate = person(
            "nj_employer_temporary_disability_insurance_contribution_rate", period
        )
        return rate * person("nj_taxable_earnings_for_state_unemployment_tax", period)
