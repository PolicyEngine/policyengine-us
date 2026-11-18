from policyengine_us.model_api import *


class wi_additional_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin additional exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/23",  # (b)3
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf",
        # Lines 10a and 10b
        # PDF pages 15-16
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=15",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # compute extra exemption amount
        p = parameters(period).gov.states.wi.tax.income
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        elderly = person("age", period) >= p.exemption.old_age
        # Wis. Stat. 71.05(23)(b)3 allows $250 for a taxpayer who "has
        # reached the age of 65" by the end of the year, and $250 for the
        # spouse who has. Age is its only condition, so a filer who can be
        # claimed as a dependent still gets it. Each spouse counts separately.
        return tax_unit.sum(filer & elderly) * p.exemption.extra
