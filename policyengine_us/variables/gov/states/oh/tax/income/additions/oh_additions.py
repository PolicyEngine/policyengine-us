from policyengine_us.model_api import *


class oh_additions(Variable):
    value_type = float
    entity = Person
    label = "Ohio additions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/communications/publications/individual_income_tax_ohio.pdf#page=2"
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=3"
        "https://cms7files1.revize.com/starkcountyoh/Document_center/Offices/Auditor/Services/Homestead%20Exemption/Ohio_Adj_Gross_Income.pdf#page=1"
    )
    defined_for = StateCode.OH
    adds = "gov.states.oh.tax.income.additions"
