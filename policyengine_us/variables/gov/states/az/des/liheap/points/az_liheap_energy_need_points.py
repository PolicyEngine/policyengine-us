from policyengine_us.model_api import *


class az_liheap_energy_need_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP energy need points"
    documentation = (
        "One benefit matrix point for each category present in the household, "
        "at most one per category: a member aged 60 or over, a member with a "
        "disability (including SSI or Social Security disability recipients), a "
        "veteran, and a child aged 6 or under."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AZ_BenefitMatrix_Heating_2026.pdf#page=1",
        # Disability definition (page 4) and Section VI.B.1.d (page 10).
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=10",
        # Section 2.4 (page 10).
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=10",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.points
        person = spm_unit.members
        age = person("age", period)
        # Section VI.B.1.d: whether any household members are "Aged six (6) and
        # under; Aged 60 and over; A veteran; or A person with a disability."
        # Worksheet: "(Only one point per category allowed)".
        elderly = spm_unit.any(age >= p.elderly_age)
        young_child = spm_unit.any(age < p.child_age_limit)
        veteran = spm_unit.any(person("is_veteran", period))
        # "Disability: A physical or mental impairment that substantially limits
        # at least one major life activity ... For the purposes of this Policy,
        # a recipient of benefits under Title II or XVI of the Social Security
        # Act, or other State-administered disability benefits, is considered
        # to categorically meet this definition" (page 4). SSI is MONTH-defined,
        # so add() sums it over the year.
        disabled = spm_unit.any(
            person("is_disabled", period)
            | (add(person, period, ["ssi"]) > 0)
            | (person("social_security_disability", period) > 0)
        )
        point = p.vulnerable_member
        return (
            where(elderly, point, 0)
            + where(disabled, point, 0)
            + where(veteran, point, 0)
            + where(young_child, point, 0)
        )
