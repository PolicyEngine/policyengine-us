from policyengine_us.model_api import *


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
        al_ded = max_(itm_ded, std_ded)
        federal_ded = tax_unit("al_federal_income_tax_deduction", period)
        exemptions = add(
            tax_unit,
            period,
            ["al_personal_exemption", "al_dependent_exemption"],
        )
        return al_ded + federal_ded + exemptions
