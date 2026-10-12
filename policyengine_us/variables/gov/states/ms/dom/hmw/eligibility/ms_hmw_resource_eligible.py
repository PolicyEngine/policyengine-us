from policyengine_us.model_api import *


class ms_hmw_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Healthier Mississippi Waiver resource eligibility rules"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2024/09/Healthier-Mississippi-Extension.pdf#page=9",
        "https://medicaid.ms.gov/wp-content/uploads/2026/02/HMW-Fact-Sheet-2026.pdf#page=1",
        "https://medicaid.ms.gov/wp-content/uploads/2024/04/20240403_MES_Gainwell_PRP-101_Member-Coverage-Description-Job_Aid_v0.1.pdf#page=5",
    )

    def formula(person, period, parameters):
        personal_resources = person("ssi_countable_resources", period)
        marital_unit = person.marital_unit
        couple = marital_unit.nb_persons() == 2
        resources = where(
            couple,
            marital_unit.sum(personal_resources),
            personal_resources,
        )
        p = parameters(period).gov.states.ms.dom.hmw.resources.limit
        return resources < where(couple, p.couple, p.individual)
