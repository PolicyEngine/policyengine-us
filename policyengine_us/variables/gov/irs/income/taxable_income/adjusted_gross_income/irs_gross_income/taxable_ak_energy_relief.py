from policyengine_us.model_api import *


class taxable_ak_energy_relief(Variable):
    value_type = float
    entity = Person
    label = "Alaska energy relief payment in gross income"
    unit = USD
    documentation = (
        "The part of ak_energy_relief in federal gross income: none of a "
        "payment from the 2022 program, whose exclusion the IRS said it would "
        "not challenge, whether the recipient got it in 2022 or in 2023; and "
        "all of each payment from 2024 on, which Alaska pays as part of the "
        "taxable dividend. A payment counts wherever the recipient lives, as "
        "the regular dividend does. See docs/validation/alaska-pfd.md."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61",
        "https://www.irs.gov/newsroom/irs-issues-guidance-on-state-tax-payments-to-help-taxpayers",
        "https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=2",
        "https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=13",
        "https://www.irs.gov/pub/irs-prior/p525--2023.pdf#page=37",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=32",
        "https://pfd.alaska.gov/payments/tax-information",
    )

    def formula(person, period, parameters):
        # No defined_for: ak_energy_relief computes nothing for people who live
        # outside Alaska, and when a dataset or user supplies a payment for
        # someone who has since moved, the payment stays in gross income.
        p = parameters(period).gov.irs.gross_income
        return where(
            p.ak_energy_relief_excluded,
            0,
            person("ak_energy_relief", period),
        )
