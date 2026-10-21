from policyengine_us.model_api import *


class ne_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP regular heating assistance eligibility"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%201%20(12-26-2020).pdf/1746#page=1",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%202%20(06-26-2022).pdf/1747#page=1",
        # 476 NAC 3-002.02.
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%203%20(12-26-2020).pdf/1748#page=1",
        # Sections 1.1 (page 5), 2.3 (page 9) and 9.1 (page 25).
        "https://liheapch.acf.gov/docs/2026/state-plans/NE_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ne_liheap_income_eligible", period)
        # 476 NAC 1-004.09 includes energy paid through rent. FY2026 plan
        # section 2.3 (page 9) says "For subsidized housing, the household must
        # be responsible for a portion of the heating payment to be eligible
        # for heating" and "For renters with utilities included in the rent,
        # the household must be responsible for a portion of the heating."
        # Modeling assumption: economic vulnerability under 1-004.06 and
        # 2-002(A) is assumed, rather than separately verified. Market-rate
        # renters with heating paid through rent are treated as responsible
        # even when the separately reported expense is zero: 476 NAC 3-002.02
        # lets the Department pay a household directly "if utilities are
        # included in rent", and plan sections 1.1 (page 5) and 9.1 (page 25)
        # list households whose utilities are included in rent among those
        # paid directly. Households receiving housing assistance or living in
        # public housing need a positive heating expense.
        # Administrative disqualifications remain unmodeled.
        # Not the repo variable has_heating_expense, which is false whenever
        # heat is included in rent.
        pays_heating_bill = spm_unit("heating_expense", period) > 0
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        housing_assisted = spm_unit("receives_housing_assistance", period)
        public_housing = spm_unit.household("is_in_public_housing", period)
        subsidized = housing_assisted | public_housing
        responsible = pays_heating_bill | (heat_in_rent & ~subsidized)
        return income_eligible & responsible
