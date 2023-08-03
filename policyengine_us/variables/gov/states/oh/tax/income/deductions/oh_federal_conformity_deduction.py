from policyengine_us.model_api import *


class oh_federal_conformity_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH federal conformity deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4"
    defined_for = StateCode.OH

    # def formula(tax_unit, period, parameters):
    #     return
