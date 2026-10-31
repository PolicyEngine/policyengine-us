from policyengine_us.model_api import *


class tx_medicaid_ltss_qit_opening_month_deposit_invalid(Variable):
    value_type = bool
    entity = Person
    label = (
        "Texas Medicaid LTSS QIT partial opening-month deposit invalidates the trust"
    )
    definition_period = MONTH
    default_value = False
    documentation = (
        "Derives the F-6820 invalidation condition for a Texas qualified "
        "income trust with a partial covered-source deposit in its opening "
        "month when subsequent full deposits have not been verified before "
        "certification. Covered deposits are clipped to the identified "
        "sources and actual deposits. A partial deposit across the covered "
        "sources invalidates the entire trust for this screen, so neither "
        "earned nor unearned deposits receive a trust exclusion. A full "
        "covered-source deposit does not require this verification. Other "
        "trust legality and deposit-validity conditions remain unmodeled."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust"

    def formula(person, period, parameters):
        state = person.household("state_code", period)
        opening_year = person("medicaid_ltss_qit_opening_year", period)
        opening_month = person("medicaid_ltss_qit_opening_month", period)
        verified = person("medicaid_ltss_qit_subsequent_full_deposits_verified", period)
        covered_income = person.empty_array()
        covered_deposits = person.empty_array()
        for source in ["earned", "unearned"]:
            gross = max_(person(f"medicaid_ltss_gross_{source}_income", period), 0)
            covered = min_(
                max_(person(f"medicaid_ltss_qit_covered_{source}_income", period), 0),
                gross,
            )
            deposits = max_(
                person(f"medicaid_ltss_{source}_income_deposited_to_qit", period), 0
            )
            deposited_covered = min_(
                max_(
                    person(
                        f"medicaid_ltss_qit_covered_{source}_income_deposited", period
                    ),
                    0,
                ),
                min_(covered, deposits),
            )
            covered_income += covered
            covered_deposits += deposited_covered
        partial_deposit = (covered_deposits > 0) & (covered_deposits < covered_income)
        return (
            (state == state.possible_values.TX)
            & (opening_year == period.start.year)
            & (opening_month == period.start.month)
            & partial_deposit
            & ~verified
        )
