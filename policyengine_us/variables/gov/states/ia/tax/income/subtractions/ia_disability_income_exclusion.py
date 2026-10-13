from policyengine_us.model_api import *


class ia_disability_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa disability income exclusion"
    unit = USD
    definition_period = YEAR
    documentation = (
        "IA 2440, for retirees under 65 who retired on permanent and total "
        "disability; Schedule 1 line 19b, code h, from 2023. The weekly $100 "
        "limit is applied as an annual cap; the employer's mandatory "
        "retirement age is not modelled."
    )
    reference = (
        # PDF pages 1-2
        "https://revenue.iowa.gov/media/4096/download?inline=#page=1",
        "https://www.legis.iowa.gov/docs/iac/rule/11-02-2022.701.302.22.pdf#page=1",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.disability_income_exclusion
        person = tax_unit.members
        eligible = person("is_tax_unit_head_or_spouse", period) & (
            person("age", period) < p.age_limit
        )
        disability_pay = person("permanent_disability_retirement_pay", period)
        # Lines 1-3: each person's pay, at most $100 a week.
        excludable = tax_unit.sum(eligible * min_(disability_pay, p.cap))
        # Line 4: reduced dollar for dollar by federal AGI above $15,000.
        agi = tax_unit("adjusted_gross_income", period)
        exclusion = max_(0, excludable - max_(0, agi - p.reduction_threshold))
        # A married person must file jointly unless the spouses did not live
        # together at any time during the year.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        lived_together = tax_unit("cohabitating_spouses", period)
        return where(separate & lived_together, 0, exclusion)
