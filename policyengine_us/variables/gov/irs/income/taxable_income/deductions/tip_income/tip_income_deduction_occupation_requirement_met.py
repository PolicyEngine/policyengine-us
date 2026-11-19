from policyengine_us.model_api import *


class tip_income_deduction_occupation_requirement_met(Variable):
    value_type = bool
    entity = Person
    label = "Occupation requirement met for the tip income deduction"
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/224#d_2_B",
        "https://www.irs.gov/irb/2026-18_IRB#TD-10044",
        # PDF pages 15-16, 18
        "https://www.irs.gov/pub/irs-drop/n-25-69.pdf#page=15",
    ]
    documentation = (
        "A person meets the occupation requirement if they received tips "
        "in a Treasury-listed tipped occupation and not in the course of "
        "a specified service trade or business. A scenario may apply the "
        "IRS transition relief for listed occupations."
    )

    def formula(person, period, parameters):
        treasury_tipped_occupation_code = person(
            "treasury_tipped_occupation_code", period
        )
        in_listed_occupation = treasury_tipped_occupation_code > 0
        p = parameters(period).gov.irs.deductions.tip_income
        if p.sstb_transition_relief:
            return in_listed_occupation
        is_sstb_legacy = person("business_is_sstb", period)
        has_sstb_self_employment_income = (
            person("sstb_self_employment_income", period) > 0
        )
        is_sstb = is_sstb_legacy | has_sstb_self_employment_income
        return in_listed_occupation & ~is_sstb
