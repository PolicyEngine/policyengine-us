from policyengine_us.model_api import *


class al_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2021/title-40/chapter-18/article-1/section-40-18-15/"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        deduction_value = (('real_estate_tax', period, p.itemized)+
                         ('mortage_interest_deduction', period, p.itemized) +
                         ('investment_intertest_deduction', period, p.itemized) +
                         ('charitable_deduction', period, p.itemized)+
                         ('taxsim_tfica', period, p.itemized) +
                         ('self_employment_tax', period, p.itemized)+
                         ('al_medical_expense_deduction', period, p.itemized) +
                         ('al_misc_deduction', period, p.itemized)
                        )
        return deduction_value
