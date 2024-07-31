from policyengine_us.model_api import *


class wi_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin exemption"
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
        # compute base exemption amount
        p = parameters(period).gov.states.wi.tax.income
        base_amount = tax_unit("exemptions_count", period) * p.exemption.base
        # compute extra exemption amount
        elderly_head = (
            tax_unit("age_head", period) >= p.exemption.old_age
        ).astype(int)
        elderly_spouse = (
            tax_unit("age_spouse", period) >= p.exemption.old_age
        ).astype(int)
        extra_amount = (elderly_head + elderly_spouse) * p.exemption.extra
        # return total exemption amount
        return base_amount + extra_amount
