from policyengine_us.model_api import *


class msp(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program benefit"
    definition_period = MONTH
    documentation = (
        "Medicare Savings Program (MSP) monthly benefit. "
        "MSP helps pay Medicare premiums for low-income beneficiaries. "
        "Three levels: QMB (100% FPL), SLMB (120% FPL), QI (135% FPL)."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"
    defined_for = "msp_eligible"

    def formula(person, period, parameters):
        return person("msp_benefit_value", period)
