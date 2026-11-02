from policyengine_us.model_api import *


class ny_inflation_refund_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York inflation refund"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606#QQQ"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        return 0

    # This refund is based on tax year 2023 returns, even though the checks were
    # mailed later. The tax effect belongs to the eligibility year.
    def formula_2023(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.inflation_refund
        agi = tax_unit("ny_agi", period)
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        # Tax Law 606(qqq): recipients, including "taxpayers filing joint
        # returns", "must not have been claimed as a dependent". This turns on
        # an actual claim, so it reads the claimed input rather than a
        # claimability helper.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        dependent_filer = tax_unit.any(filer & claimed)

        amount = select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.head_of_household.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.surviving_spouse.calc(agi, right=True),
            ],
        )
        return where(dependent_filer, 0, amount)

    def formula_2024(tax_unit, period, parameters):
        return 0
