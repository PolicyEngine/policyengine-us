from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    eitc_amount_for_child_count,
    eitc_filer_identification_met,
    eitc_section_911_eligible,
)


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition and, from 2020, the IRC 32(m) Social Security number limitation ignored; the maximum age condition and the bar on section 911 claimants still apply."
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
        # 2. the limitation under § 32(m)". Recompose the federal EITC without
        # the minimum age, accepting an ITIN or any Social Security number;
        # the maximum age in § 32(c)(1)(A)(ii)(II) and other federal § 32
        # rules (investment income, section 911) still apply.
        person = tax_unit.members
        child_count = tax_unit("md_eitc_child_count", period)
        has_child = child_count > 0
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        below_max_age = person("age", period) <= max_age
        meets_max_age = has_child | tax_unit.any(below_max_age & is_filer_or_spouse)
        # The federal phase-in and phase-out, with the qualifying children
        # Maryland takes into account.
        amount = eitc_amount_for_child_count(tax_unit, period, parameters, child_count)
        investment_eligible = tax_unit("eitc_investment_income_eligible", period)
        p = parameters(period).gov.states.md.tax.income.credits.eitc
        filer_identified = eitc_filer_identification_met(
            tax_unit, period, p.itin_eligible
        )
        # § 32(c)(1)(C): no credit for an individual who claims the benefits
        # of section 911. The 2025 Resident Booklet (Instruction 18) waives the
        # minimum age only for a filer who is "otherwise eligible for the
        # federal credit for those without a qualifying child".
        section_911_eligible = eitc_section_911_eligible(tax_unit, period)
        return (
            amount
            * investment_eligible
            * filer_identified
            * section_911_eligible
            * meets_max_age
        )
