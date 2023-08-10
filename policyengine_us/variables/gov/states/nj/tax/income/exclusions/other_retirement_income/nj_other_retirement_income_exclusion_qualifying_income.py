from policyengine_us.model_api import *


class nj_other_retirement_income_exclusion_qualifying_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Other Retirement Income Exclusion Qualifying Income"
    unit = USD
    documentation = (
        "New Jersey other retirement income exclusion qualifying income"
    )
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get the pension/retirement exclusion portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        # Get the total income (line 27) for head and spouse above age threshold.
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        joint = filing_status == status.JOINT
        age_eligible = person("age", period) >= p.age_threshold
        qualifying_head = age_eligible * is_head
        qualifying_spouse = age_eligible * is_spouse
        gross_income = person("irs_gross_income", period)
        exempt_interest_income = person("tax_exempt_interest_income", period)
        exempt_pension_income = person("tax_exempt_pension_income", period)
        fed_taxable_ss = person("taxable_social_security", period)
        person_qualifying_income = (
            gross_income
            - exempt_interest_income
            - exempt_pension_income
            - fed_taxable_ss
        )
        return where(
            joint,
            tax_unit.sum(
                person_qualifying_income
                * (qualifying_head + qualifying_spouse)
            ),
            tax_unit.sum(person_qualifying_income * qualifying_head),
        )
