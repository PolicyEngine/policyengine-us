from policyengine_us.model_api import *


class medicaid_ltss_qit_adjusted_needs_based_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS needs-based unearned income remaining outside a qualified income trust"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Computes each person's own needs-based unearned income outside "
        "the qualified income trust from gross needs-based income and "
        "its deposited source component. Deposited needs-based income "
        "cannot exceed gross needs-based income or total unearned "
        "deposits; the remaining needs-based amount cannot exceed "
        "remaining unearned income. This preserves the general exclusion "
        "carve-out when deposited source classifications are incomplete. "
        "Washington has no qualified income trust exception under "
        "42 USC 1396p(d)(4)(B)(iii), and WAC 182-513-1340 lists no trust "
        "deposit among its exclusions, so deposits leave its needs-based "
        "income unchanged."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://www.law.cornell.edu/uscode/text/42/1396p#d_4_B",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340",
    )

    def formula(person, period, parameters):
        gross_unearned = max_(person("medicaid_ltss_gross_unearned_income", period), 0)
        gross_needs_based = min_(
            max_(person("medicaid_ltss_needs_based_income", period), 0), gross_unearned
        )
        unearned_deposits = min_(
            max_(person("medicaid_ltss_unearned_income_deposited_to_qit", period), 0),
            gross_unearned,
        )
        needs_based_deposits = min_(
            max_(
                person("medicaid_ltss_needs_based_income_deposited_to_qit", period), 0
            ),
            min_(gross_needs_based, unearned_deposits),
        )
        state = person.household("state_code", period)
        return where(
            state == state.possible_values.WA,
            gross_needs_based,
            min_(
                max_(gross_needs_based - needs_based_deposits, 0),
                person("medicaid_ltss_qit_adjusted_unearned_income", period),
            ),
        )
