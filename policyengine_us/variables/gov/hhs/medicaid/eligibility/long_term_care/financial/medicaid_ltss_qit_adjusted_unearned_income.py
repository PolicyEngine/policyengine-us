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
        "is subtracted from that extension to avoid a duplicate exclusion."
    )
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
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
        return max_(income - deposits - additional_exclusion, 0)
