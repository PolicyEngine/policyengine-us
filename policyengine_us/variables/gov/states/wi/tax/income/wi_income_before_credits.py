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

        # Note: Wisconsin uses joint rates for surviving spouse
        rates_dict = {
            "single": p.rates.single,
            "joint": p.rates.joint,
            "surviving_spouse": p.rates.joint,  # Uses joint rates
            "separate": p.rates.separate,
            "head_of_household": p.rates.head_of_household,
        }

        return select_filing_status_value(fstatus, rates_dict, taxinc)
