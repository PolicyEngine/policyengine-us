from policyengine_us.model_api import *


class de_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Delaware LIHEAP summer cooling electric benefit"
    defined_for = StateCode.DE
    reference = (
        # PDF pages 12-13
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=12",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2027/state-plans/DE_Plan_2027.pdf#page=11",
        "https://dhss.delaware.gov/dss/division-of-social-services/utility-assistance/",
        # Historical manual sections 303.1-303.2 and 416.
        # PDF pages 21-22, 32
        "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=21",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.cooling
        # Plan 3.5: the benefit "is distributed only to the LIHEAP eligible
        # households"; DHSS: "Eligibility requires prior application for
        # LIHEAP during the program year". Manual 416 requires responsibility
        # for a heating bill, which de_liheap_eligible checks.
        liheap_eligible = spm_unit("de_liheap_eligible", period)
        # heating_type is a required input: an unspecified type is
        # ineligible, including when heat is included in rent.
        heating_type = spm_unit("heating_type", period)
        heating_type_reported = heating_type != heating_type.possible_values.UNSPECIFIED
        # Plan 3.3-3.4: targeted to members "sixty or older, disabled,
        # children five and under", and members with chronic breathing
        # conditions, which have no input.
        person = spm_unit.members
        age = person("age", period)
        vulnerable = (
            (age >= p.elderly_age)
            | (age < p.child_age_limit)
            | person("is_disabled", period)
        )
        has_vulnerable_member = spm_unit.any(vulnerable)
        # Manual 303.1: the benefit is "paid to their electric company".
        has_cooling_expense = spm_unit("has_cooling_expense", period)
        has_electric_bill = spm_unit("pre_subsidy_electricity_expense", period) > 0
        return (
            liheap_eligible
            & heating_type_reported
            & has_vulnerable_member
            & has_cooling_expense
            & has_electric_bill
        )
