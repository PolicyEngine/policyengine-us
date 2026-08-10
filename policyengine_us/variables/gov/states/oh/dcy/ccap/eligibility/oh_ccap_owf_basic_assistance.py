from policyengine_us.model_api import *


class oh_ccap_owf_basic_assistance(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Ohio Works First basic assistance for Ohio CCAP income"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03"
    # 5180:2-16-03(H)(3)(j) counts Ohio Works First cash assistance as
    # unearned income. This is a bare input defaulting to zero: reading the
    # computed OWF benefit would recreate the CCAP-TANF circular dependency
    # through childcare_expenses, and OWF payment standards leave enrolled
    # families well below the 145% intake standard and the 100%-FPG
    # zero-copay band, so the default does not change modeled results.
