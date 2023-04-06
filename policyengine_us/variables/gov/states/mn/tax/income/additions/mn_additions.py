from policyengine_us.model_api import *


class mn_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf"
    )
    defined_for = StateCode.MN
    adds = "gov.states.mn.tax.income.additions.sources"
