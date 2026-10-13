from policyengine_us.model_api import *


class ny_disability_income_exclusion(Variable):
    value_type = float
    entity = Person
    label = "New York disability income exclusion"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Form IT-221, for people under 65 who retired on permanent and total "
        "disability. The weekly $100 limit is applied as an annual cap; the "
        "employer's mandatory retirement age is not modelled."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/612",
        # PDF pages 1-2
        "https://www.tax.ny.gov/pdf/2024/inc/it221i_2024.pdf#page=1",
    )
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.disability_income_exclusion
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # A married person filing separately qualifies only if the spouses
        # lived apart all year.
        filing_eligible = ~(separate & tax_unit("cohabitating_spouses", period))
        eligible = (
            person("is_tax_unit_head_or_spouse", period)
            & (person("age", period) < p.age_limit)
            & filing_eligible
        )
        disability_pay = eligible * person(
            "permanent_disability_retirement_pay", period
        )
        # Lines 1-10: each person's pay at most $100 a week, reduced dollar
        # for dollar by federal AGI above $15,000.
        excludable = tax_unit.sum(min_(disability_pay, p.cap))
        agi = tax_unit("adjusted_gross_income", period)
        exclusion = max_(0, excludable - max_(0, agi - p.reduction_threshold))
        # Line 11: spouses share it in proportion to their disability pay.
        total_pay = tax_unit.sum(disability_pay)
        share = np.divide(
            disability_pay,
            total_pay,
            out=np.zeros_like(total_pay),
            where=total_pay > 0,
        )
        # Each person's disability and pension exclusions together are
        # limited to $20,000; an unused part of a spouse's limit can't be used.
        pension_exclusion = person("ny_pension_exclusion", period)
        room = max_(0, p.combined_limit - pension_exclusion)
        return min_(exclusion * share, room)
