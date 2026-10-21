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
    # PDF pages 1-3
    reference = "https://www.revenue.wi.gov/TaxForms2024/2024-Schedule2440Wf.pdf#page=1"
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
        # A claimant married at the end of the year must file a joint
        # return: no separate return, and no head of household return by a
        # spouse who is separated but still married.
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separated = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("is_separated", period)
        )
        married_not_joint = (filing_status == status.SEPARATE) | (
            (filing_status != status.JOINT) & separated
        )
        return where(married_not_joint, 0, exclusion)
