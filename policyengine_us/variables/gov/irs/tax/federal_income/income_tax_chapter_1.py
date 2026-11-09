from policyengine_us.model_api import *


class income_tax_chapter_1(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Chapter 1 federal income tax after nonrefundable credits"
    documentation = (
        "Federal income tax liability under chapter 1 after nonrefundable "
        "credits and before refundable credits, including investment credit "
        "recapture and the additional tax on early retirement distributions. "
        "Excludes chapter 2A net investment income tax and chapter 21 "
        "unreported payroll tax. Refundable credits are payments applied to "
        "the liability, not reductions of the liability."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1",
        "https://www.law.cornell.edu/uscode/text/26/1411",
        "https://www.law.cornell.edu/uscode/text/26/6401#b",
        "https://www.law.cornell.edu/uscode/text/42/401",
    )

    def formula(tax_unit, period, parameters):
        if parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
            return 0

        added_components = add(
            tax_unit,
            period,
            [
                "income_tax_before_credits",
                "recapture_of_investment_credit",
                "qualified_retirement_penalty",
            ],
        )
        nonrefundable_credits = tax_unit(
            "income_tax_capped_non_refundable_credits", period
        )
        return added_components - nonrefundable_credits
