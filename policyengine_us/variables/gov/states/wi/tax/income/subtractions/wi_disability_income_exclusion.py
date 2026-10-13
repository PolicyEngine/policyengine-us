from policyengine_us.model_api import *


class wi_disability_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin disability income exclusion"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Schedule 2440W, for retirees under 65 who retired on permanent and "
        "total disability. The weekly $100 limit is applied as an annual cap; "
        "the employer's mandatory retirement age is not modelled."
    )
    reference = (
        "https://www.revenue.wi.gov/TaxForms2024/2024-Schedule2440Wf.pdf#page=1",
        "https://www.revenue.wi.gov/TaxForms2024/2024-Schedule2440Wf.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2024/2024-Schedule2440Wf.pdf#page=3",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.subtractions.disability_income
        person = tax_unit.members
        eligible = person("is_tax_unit_head_or_spouse", period) & (
            person("age", period) < p.age_limit
        )
        disability_pay = person("permanent_disability_retirement_pay", period)
        # Lines 1-4: each person's disability pay, at most $100 a week.
        excludable = tax_unit.sum(eligible * min_(disability_pay, p.cap))
        # Line 5: reduced dollar for dollar by income above $15,000.
        agi = tax_unit("adjusted_gross_income", period)
        reduction = max_(0, agi - p.reduction_threshold)
        exclusion = max_(0, excludable - reduction)
        # A married claimant must file a joint return.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(separate, 0, exclusion)
