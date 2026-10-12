from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.credits.cdcc.count_cdcc_eligible import (
    count_cdcc_eligible,
)


class ma_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA dependent care credit"
    unit = USD
    definition_period = YEAR
    # Former G.L. c. 62 section 6(x) (added by St. 2021, c. 24, section 29;
    # replaced by the Child and Family Tax Credit for 2023+).
    reference = "https://web.archive.org/web/20220517114137/https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section6"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.credits.dependent_care
        # The credit equals the IRC 21 employment-related expenses:
        # childcare plus care for a disabled qualifying individual of any
        # age, capped by the number of qualifying individuals.
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        count_cdcc_eligible = min_(
            tax_unit("count_cdcc_eligible", period), p.dependent_cap
        )
        # Line 1.
        capped_expenses = min_(expenses, p.amount * count_cdcc_eligible)
        # Skip lines 2 and 3, which are done in intermediate steps.
        # Line 4: Smallest of lines 1, 2, 3.
        amount_if_eligible = min_(
            capped_expenses, tax_unit("min_head_spouse_earned", period)
        )
        # Skip line 5 for prior-year expenses.
        # The credit imports the IRC 21 rules, including the 21(e)(2)
        # joint-return requirement and the 21(e)(4) separated-taxpayer
        # exception.
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        return eligible * amount_if_eligible
