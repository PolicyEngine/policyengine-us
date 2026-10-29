from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    eitc_section_911_eligible,
    federal_eitc_tax_unit,
    pro_forma_federal_eitc,
)


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition and, from 2020, the IRC 32(m) Social Security number limitation ignored; the maximum age condition, the investment income limit and the bar on section 911 claimants still apply, as does any reform of the federal credit. Like the federal credit, it is computed on the AGI of the return as filed; unlike it, it applies no take-up, filing condition or separate-filer rule."
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_C",
        # 2025 Maryland Resident Booklet, Instruction 18.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=22",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Per Md. Code Tax-Gen. § 10-704(c)(3)(i), for an individual without
        # a qualifying child the § 32 credit is calculated without regard to
        # "1. the minimum age requirement under § 32(c)(1)(A)(ii)(II) ... or
        # 2. the limitation under § 32(m)". Evaluate the federal EITC with its
        # eligibility replaced by the conditions below, accepting an ITIN or
        # any Social Security number; the maximum age in
        # § 32(c)(1)(A)(ii)(II) and other federal § 32 rules (investment
        # income, section 911) still apply, and so does any reform of the
        # federal credit.
        # The tax units with an ITIN or any Social Security number accepted
        # (when Maryland waives 32(m)), so the qualifying children are those
        # of the federal formulas, reforms included.
        federal = federal_eitc_tax_unit(tax_unit, period)
        person = federal.members
        has_child = federal("eitc_child_count", period) > 0
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        below_max_age = person("age", period) <= max_age
        meets_max_age = has_child | federal.any(below_max_age & is_filer_or_spouse)
        # § 32(c)(1)(C): no credit for an individual who claims the benefits
        # of section 911. The 2025 Resident Booklet (Instruction 18) waives the
        # minimum age only for a filer who is "otherwise eligible for the
        # federal credit for those without a qualifying child".
        eligible = (
            federal("eitc_investment_income_eligible", period)
            & federal("filer_meets_eitc_identification_requirements", period)
            & eitc_section_911_eligible(federal, period)
            & meets_max_age
        )
        return pro_forma_federal_eitc(federal, period, "md_pro_forma_eitc", eligible)
