from policyengine_us.model_api import *


class ny_ui_partial_benefit_credit(Variable):
    value_type = float
    entity = Person
    label = "NY UI partial benefit credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/525"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        weekly_benefit_rate = person("ny_ui_weekly_benefit_rate", period)
        return np.ceil(
            max_(
                p.partial_benefit_credit_rate * weekly_benefit_rate,
                p.partial_benefit_credit_min,
            )
        )
