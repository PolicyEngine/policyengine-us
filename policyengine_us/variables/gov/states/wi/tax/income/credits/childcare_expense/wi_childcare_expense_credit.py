from policyengine_us.model_api import *


class wi_childcare_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin childcare expense credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/9g",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income
        p_wi = p.credits.childcare_expense

        wi_max_expense = p_wi.max_expense

        if wi_max_expense > 0:
            # For 2024+, Wisconsin Act 101 of 2023 sets its own expense cap of
            # $10,000 per qualifying individual (§71.07(9g)(c)5), replacing the
            # federal per-individual limit under IRC §21(c).
            count_eligible = tax_unit("capped_count_cdcc_eligible", period)
            wi_expense_limit = wi_max_expense * count_eligible
            raw_expenses = tax_unit("tax_unit_childcare_expenses", period)
            # Cap to WI limit, then also cap to min head/spouse earned (§21(d))
            wi_capped_expenses = min_(raw_expenses, wi_expense_limit)
            wi_relevant_expenses = min_(
                wi_capped_expenses,
                tax_unit("min_head_spouse_earned", period),
            )
            cdcc_rate = tax_unit("cdcc_rate", period)
            return wi_relevant_expenses * cdcc_rate * p_wi.fraction
        else:
            # Pre-2024: Wisconsin matches the potential federal credit
            us_cdcc = tax_unit("cdcc_potential", period)
            return us_cdcc * p_wi.fraction
