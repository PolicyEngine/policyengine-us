from policyengine_us.model_api import *


class mi_disabled_exemption_eligible_person(Variable):
    value_type = float
    entity = Person
    label = "Eligible person for the Michigan disabled exemptions"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
    )

    def formula(person, period, parameters):
        blind = person("is_blind", period)
        deaf = person("is_deaf", period)
        # Only totally disabled people under a certain age are eligible
        totally_disabled = person(
            "is_permanently_and_totally_disabled", period
        )
        p = parameters(period).gov.states.mi.tax.income.exemptions.disabled
        age_eligible = person("age", period) < p.age_limit
        totally_disabled_eligible = totally_disabled & age_eligible

        return blind | deaf | totally_disabled_eligible
