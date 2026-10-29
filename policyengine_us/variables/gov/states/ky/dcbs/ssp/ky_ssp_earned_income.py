from policyengine_us.model_api import *


class ky_ssp_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Kentucky SSP earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLIVA.pdf#page=188",
    )
    documentation = (
        "Kentucky SSP own earned income, retaining the existing wage-limited "
        "pretax premium exclusion. A loss in one modeled self-employment "
        "source cannot reduce wages or another business source. Inputs may "
        "already aggregate multiple businesses; their separate profits and "
        "Kentucky-specific expense adjustments are not exposed."
    )

    def formula(person, period, parameters):
        sources = parameters(
            period
        ).gov.states.ky.dcbs.ssp.earned.self_employment_sources
        # MS 2450 C.8(b) disallows losses from one business against another.
        # Keep Kentucky's list separate from SSI's signed NESE aggregation.
        business_income = sum(max_(person(source, period), 0) for source in sources)
        wages = max_(person("employment_income", period), 0)
        pretax_premiums = max_(person("pre_tax_health_insurance_premiums", period), 0)
        return wages - min_(wages, pretax_premiums) + business_income
