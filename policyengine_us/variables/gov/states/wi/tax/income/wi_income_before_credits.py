from policyengine_us.model_api import *


class wi_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        taxinc = tax_unit("wi_taxable_income", period)
        fstatus = tax_unit("filing_status", period)
        p = parameters(period).gov.states.wi.tax.income
        return select(
            [
                fstatus == fstatus.possible_values.SINGLE,
                fstatus == fstatus.possible_values.JOINT,
                fstatus == fstatus.possible_values.WIDOW,
                fstatus == fstatus.possible_values.SEPARATE,
                fstatus == fstatus.possible_values.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rates.single.calc(taxinc),
                p.rates.joint.calc(taxinc),
                p.rates.joint.calc(taxinc),
                p.rates.separate.calc(taxinc),
                p.rates.head_of_household.calc(taxinc),
            ],
        )
