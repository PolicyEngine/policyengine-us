from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class al_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf"  # 2022 Form 40A Booklet
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        itm_ded = tax_unit("al_itemized_deductions", period)
        std_ded = tax_unit("al_standard_deduction", period)
        method = tax_unit("state_deduction_method", period)
        itemizes = state_itemization_uses_itemized(method, itm_ded > std_ded)
        al_ded = where(itemizes, itm_ded, std_ded)
        federal_ded = tax_unit("al_federal_income_tax_deduction", period)
        exemptions = add(
            tax_unit,
            period,
            ["al_personal_exemption", "al_dependent_exemption"],
        )
        plan_529 = tax_unit("al_529_plan_deduction", period)
        return al_ded + federal_ded + exemptions + plan_529
