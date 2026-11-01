from policyengine_us.model_api import *


class ok_count_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Count of Oklahoma exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf#page=9",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=9",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.exemptions
        # special exemption AGI eligibility (excluding Roth conversion income included in federal AGI per Form 511 instructions)
        person = tax_unit.members
        is_not_dependent = ~person("is_tax_unit_dependent", period)
        roth_conversions = tax_unit.sum(
            person("taxable_roth_conversions", period) * is_not_dependent
        )
        fagi = tax_unit("adjusted_gross_income", period) - roth_conversions
        filing_status = tax_unit("filing_status", period)
        agi_eligible = fagi <= p.special_agi_limit[filing_status]
        # head exemptions
        age_eligible = tax_unit("age_head", period) >= p.special_age_minimum
        head_exemptions = where(tax_unit("blind_head", period), 2, 1) + where(
            agi_eligible & age_eligible, 1, 0
        )
        # spouse exemptions
        age_eligible = tax_unit("age_spouse", period) >= p.special_age_minimum
        spouse_exemptions = where(
            filing_status == filing_status.possible_values.JOINT,
            (
                where(tax_unit("blind_spouse", period), 2, 1)
                + where(agi_eligible & age_eligible, 1, 0)
            ),
            0,
        )
        # dependent exemptions
        dependents = tax_unit("tax_unit_dependents", period)
        # total number of exemptions
        return head_exemptions + spouse_exemptions + dependents
