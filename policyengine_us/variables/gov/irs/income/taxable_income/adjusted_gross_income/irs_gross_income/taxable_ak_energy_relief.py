from policyengine_us.model_api import *


class taxable_ak_energy_relief(Variable):
    value_type = float
    entity = Person
    label = "Alaska energy relief payment in gross income"
    unit = USD
    documentation = (
        "The part of ak_energy_relief in federal gross income: none of the "
        "2022 payment, whose exclusion the IRS said it would not challenge, "
        "and all of each later payment, which Alaska pays as part of the "
        "taxable dividend. See docs/validation/alaska-pfd.md."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61",
        "https://www.irs.gov/newsroom/irs-issues-guidance-on-state-tax-payments-to-help-taxpayers",
        "https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=32",
        "https://pfd.alaska.gov/payments/tax-information",
    )
    defined_for = StateCode.AK

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income
        return where(
            p.ak_energy_relief_excluded,
            0,
            person("ak_energy_relief", period),
        )
