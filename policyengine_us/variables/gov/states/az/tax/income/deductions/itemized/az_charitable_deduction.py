from policyengine_us.model_api import *


class charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Charitable deduction"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://casetext.com/statute/arizona-revised-statutes/title-43-taxation-of-income/chapter-10-individuals/article-5-credits/section-43-1088-effective-until-ninety-one-days-after-adjournment-credit-for-contribution-to-qualifying-charitable-organizations-definitions"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.deduction.itemized.charity
        filing_status = tax_unit("filing_status", period)
        cash_donations_qualifying_organization = add(
            tax_unit,
            period,
            ["qualifying_charitable_cash_donations_qualifying_organization"],
        )
        # voluntary cash contributions to a qualifying charitable organization (Subsection A)
        # the name above may need some modifications
        ceiling_cash_donations_qualifying_organization = (
            p.ceiling.qualifying_organization[filling_status]
        )
        capped_cash_donations_qualifying_organization = min_(
            ceiling_cash_donations_qualifying_organization,
            cash_donations_qualifying_organization,
        )

        cash_donations_qualifying_foster = add(
            tax_unit,
            period,
            ["qualifying_charitable_cash_donations_foster_organization"],
        )
        # need to modify "qualifying_charitable_cash_donations_foster_organization"
        # it is from section B in the reference
        ceiling_cash_donations_qualifying_foster = p.ceiling.qualifying_foster[
            filling_status
        ]
        capped_cash_donations_qualifying_foster = min_(
            cash_donations_qualifying_foster,
            ceiling_cash_donations_qualifying_foster,
        )

        return (
            capped_cash_donations_qualifying_foster
            + capped_cash_donations_qualifying_organization
        )
