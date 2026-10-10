from policyengine_us.model_api import *


class ok_count_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Count of Oklahoma exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf#page=9",
        # 2025 Form 511 instructions, item F (Exemptions).
        # PDF pages 8-9
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=8",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
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
        # Regular exemptions: "You may claim an exemption for yourself if you
        # cannot be claimed as a dependent on another person's return", and
        # for a joint spouse who "cannot be claimed as a dependent on another
        # person's return" (Form 511 instructions, item F). The special (65 or
        # older) and blind exemptions are separate boxes with no such bar.
        # Each filer's own regular exemption follows that filer's own flag.
        claimed = person("claimed_as_dependent_on_another_return", period)
        head_claimed = tax_unit.any(person("is_tax_unit_head", period) & claimed)
        spouse_claimed = tax_unit.any(person("is_tax_unit_spouse", period) & claimed)
        head_regular = where(head_claimed, 0, 1)
        spouse_regular = where(spouse_claimed, 0, 1)
        # head exemptions
        age_eligible = tax_unit("age_head", period) >= p.special_age_minimum
        head_exemptions = (
            head_regular
            + where(tax_unit("blind_head", period), 1, 0)
            + where(agi_eligible & age_eligible, 1, 0)
        )
        # spouse exemptions
        age_eligible = tax_unit("age_spouse", period) >= p.special_age_minimum
        spouse_exemptions = where(
            filing_status == filing_status.possible_values.JOINT,
            (
                spouse_regular
                + where(tax_unit("blind_spouse", period), 1, 0)
                + where(agi_eligible & age_eligible, 1, 0)
            ),
            0,
        )
        # dependent exemptions: each "dependent, as defined in IRC Sec. 152"
        # (item F), and a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has none (IRC 152(b)(1)).
        dependents = tax_unit("tax_unit_dependents", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        # total number of exemptions
        return (
            head_exemptions
            + spouse_exemptions
            + where(filer_is_dependent, 0, dependents)
        )
