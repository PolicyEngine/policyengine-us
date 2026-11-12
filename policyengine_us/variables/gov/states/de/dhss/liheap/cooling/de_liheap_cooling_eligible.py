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
        # Historical manual sections 303.1-303.2 and the SCAP eligibility chart.
        # PDF pages 21-22, 100
        "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=21",
        "https://liheappm.acf.gov/sites/default/files/private/congress/profiles/2024/FY2024_Delaware_Profile.pdf",
        "https://liheappm.acf.gov/sites/default/files/private/congress/profiles/2025/FY%202025%20Delaware%20Profile.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.cooling
        # Plan 3.5: the benefit "is distributed only to the LIHEAP eligible
        # households"; DHSS: "Eligibility requires prior application for
        # LIHEAP during the program year". The SCAP chart (manual page 100)
        # defines LIHEAP eligibility as "Purchase Source of Heating or Cooling",
        # and plan 3.3 sets no cooling policy for subsidized renters or renters
        # with utilities in the rent. So the household and income test applies
        # without the heating responsibility test of regular heating, and the
        # cooling cost below is the purchased source of cooling.
        income_eligible = spm_unit("de_liheap_income_eligible", period)
        # PolicyEngine convention, not a Delaware rule: heating_type is a
        # required input, so an unspecified type is ineligible.
        heating_type = spm_unit("heating_type", period)
        heating_type_reported = heating_type != heating_type.possible_values.UNSPECIFIED
        # Plan 3.3-3.4: targeted to members "sixty or older, disabled,
        # children five and under", and members with chronic breathing
        # conditions, which have no input. The plans let the State extend the
        # benefit to every LIHEAP applicant when funds allow. HHS profiles count
        # more cooling households than households with a targeted member in
        # FY2023 and FY2024, and 88 cooling households in FY2025. No decision
        # for 2026 was found, so the targeted rule applies.
        person = spm_unit.members
        age = person("age", period)
        vulnerable = (
            (age >= p.elderly_age)
            | (age < p.child_age_limit)
            | person("is_disabled", period)
        )
        has_vulnerable_member = spm_unit.any(vulnerable)
        # Paying for cooling, the input every state's cooling assistance uses.
        # Every household is assumed to hold an active electric account.
        has_cooling_expense = spm_unit("has_cooling_expense", period)
        return (
            income_eligible
            & heating_type_reported
            & has_vulnerable_member
            & has_cooling_expense
        )
