from policyengine_us.model_api import *


class tip_income_deduction_occupation_requirement_met(Variable):
    value_type = bool
    entity = Person
    label = "Occupation requirement met for the tip income deduction"
    definition_period = YEAR
    reference = [
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf",
        "https://www.irs.gov/irb/2025-42_IRB",
    ]
    documentation = (
        "A person meets the occupation requirement if they received tips "
        "in a Treasury-listed tipped occupation and not in the course of "
        "a specified service trade or business."
    )

    def formula(person, period, _parameters):
        treasury_tipped_occupation_code = person(
            "treasury_tipped_occupation_code", period
        )
        is_sstb_legacy = person("business_is_sstb", period)
        has_sstb_self_employment_income = (
            person("sstb_self_employment_income", period) > 0
        )
        is_sstb = is_sstb_legacy | has_sstb_self_employment_income
        return (treasury_tipped_occupation_code > 0) & ~is_sstb
