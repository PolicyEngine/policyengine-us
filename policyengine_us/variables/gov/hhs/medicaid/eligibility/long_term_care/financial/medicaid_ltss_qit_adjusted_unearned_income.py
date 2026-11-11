from policyengine_us.model_api import *


class medicaid_ltss_qit_adjusted_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS unearned income after qualified income trust exclusions"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Each person's own gross unearned income after qualified income "
        "trust exclusions, before other Medicaid LTSS income exclusions. "
        "Actual valid deposits are excluded in ordinary months. Texas "
        "excludes entire identified sources in the trust's opening month "
        "after a partial covered-source deposit and verification of "
        "subsequent full deposits. The deposited covered-source component "
        "is subtracted from that extension to avoid a duplicate exclusion. "
        "Under F-6820, an unverified partial opening-month deposit "
        "invalidates the trust for this screen: neither income stream "
        "receives a deposited-income exclusion. Full covered deposits "
        "retain their actual-deposit exclusion without that verification. "
        "Washington covers nursing facility services for the medically "
        "needy, so 42 USC 1396p(d)(4)(B)(iii) gives it no qualified income "
        "trust exception. WAC 182-513-1340 lists no trust deposit among "
        "its exclusions, so deposits leave Washington income unchanged."
    )
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
        "https://www.law.cornell.edu/uscode/text/42/1396p#d_4_B",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1395",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340",
    )

    def formula(person, period, parameters):
        income = max_(person("medicaid_ltss_gross_unearned_income", period), 0)
        deposits = min_(
            max_(person("medicaid_ltss_unearned_income_deposited_to_qit", period), 0),
            income,
        )
        covered = min_(
            max_(person("medicaid_ltss_qit_covered_unearned_income", period), 0),
            income,
        )
        covered_deposits = min_(
            max_(
                person("medicaid_ltss_qit_covered_unearned_income_deposited", period),
                0,
            ),
            min_(covered, deposits),
        )
        opening_month = person(
            "tx_medicaid_ltss_qit_opening_month_exclusion_applies", period
        )
        additional_exclusion = where(opening_month, covered - covered_deposits, 0)
        invalid_opening_deposit = person(
            "tx_medicaid_ltss_qit_opening_month_deposit_invalid", period
        )
        state = person.household("state_code", period)
        return where(
            invalid_opening_deposit | (state == state.possible_values.WA),
            income,
            max_(income - deposits - additional_exclusion, 0),
        )
