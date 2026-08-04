from policyengine_us.model_api import *


class ms_hmw_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Healthier Mississippi Waiver income eligibility rules"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2024/09/Healthier-Mississippi-Extension.pdf#page=9",
        "https://medicaid.ms.gov/wp-content/uploads/2026/02/HMW-Fact-Sheet-2026.pdf#page=2",
        "https://medicaid.ms.gov/wp-content/uploads/2024/04/20240403_MES_Gainwell_PRP-101_Member-Coverage-Description-Job_Aid_v0.1.pdf#page=5",
    )

    def formula(person, period, parameters):
        personal_income = person(
            "medicaid_optional_senior_or_disabled_countable_income", period
        )
        marital_unit = person.marital_unit
        couple = marital_unit.nb_persons() == 2
        income = where(couple, marital_unit.sum(personal_income), personal_income)
        state_group = person.household("state_group_str", period)
        fpg = parameters(period).gov.hhs.fpg
        unit_fpg = fpg.first_person[state_group] + (
            couple * fpg.additional_person[state_group]
        )
        p = parameters(period).gov.states.ms.dom.hmw.income.limit
        return income <= p.rate * unit_fpg
