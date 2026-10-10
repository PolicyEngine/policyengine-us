from policyengine_us.model_api import *


class ca_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "CalEITC eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.",
        "https://www.ftb.ca.gov/forms/2024/2024-3514-booklet.html",
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.pdf#page=6",
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_A_ii",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income

        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)

        meets_age_requirements = tax_unit.any(
            (age >= p.eligibility.age.min)
            & (age <= p.eligibility.age.max)
            & ~is_dependent
        )

        eitc_investment_income = tax_unit("eitc_relevant_investment_income", period)

        meets_investment_income_requirements = (
            eitc_investment_income <= p.eligibility.max_investment_income
        )

        # FTB 3514 Step 1 requires federal AGI below the exclusive income limit.
        # Compare supplied income without optional whole-dollar return rounding.
        federal_agi = tax_unit("adjusted_gross_income", period)
        meets_agi_requirements = federal_agi < p.phase_out.final.end

        # RTC 17052 keeps the IRC 32(c)(1)(A)(ii)(III) rule: without a
        # qualifying child, the filer must not be another taxpayer's
        # dependent (FTB 3514, Step 4, question f). FTB 3514 skips that
        # question on a joint return because a married filer can be claimed
        # only when the joint return seeks just a refund of withholding; as
        # for the federal credit, a joint return on which either spouse can
        # be claimed gets no credit without a qualifying child.
        has_qualifying_child = tax_unit.any(
            person("ca_is_qualifying_child_for_caleitc", period)
        )
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        meets_dependency_requirements = has_qualifying_child | ~dependent_elsewhere

        return (
            meets_age_requirements
            & meets_investment_income_requirements
            & meets_agi_requirements
            & meets_dependency_requirements
        )
