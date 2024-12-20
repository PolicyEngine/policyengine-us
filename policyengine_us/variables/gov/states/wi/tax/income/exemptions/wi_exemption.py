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

    adds = ["wi_base_exemption", "wi_additional_exemption"]
