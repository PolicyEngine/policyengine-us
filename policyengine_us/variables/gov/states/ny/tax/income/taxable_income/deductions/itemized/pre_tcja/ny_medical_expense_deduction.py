from policyengine_us.model_api import *


class ny_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pdf/2025/inc/it196_2025_fill_in.pdf#page=1",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    pre-TCJA federal rules. Pre-TCJA 26 U.S.C. 213(a) allowed medical and
    dental expenses only above 10% of federal AGI; NY does not follow the
    7.5% floor that Public Law 115-97 § 11027 set for federal returns.
    Form IT-196 lines 1-4 apply this floor to federal AGI (Form IT-201 or
    IT-203 line 19; line 19a, recomputed federal AGI, in 2020-2022, which
    PolicyEngine does not distinguish from federal AGI).
    """

    def formula(tax_unit, period, parameters):
        # NY uses pre-TCJA rules: medical expenses are deductible above 10%
        # of AGI (not the federal 7.5% floor after 2017)
        p = parameters(period).gov.states.ny.tax.income.deductions.itemized.medical
        expenses = tax_unit("itemized_medical_expenses", period)
        medical_floor = p.floor * tax_unit("positive_agi", period)
        return max_(0, expenses - medical_floor)
