from policyengine_us.model_api import *

class mt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MT CTC"
    definition_period = YEAR
    unit = USD
    documentation = "Montana Child Tax Credit"
    reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # int number of children
        # bool proof of earned income & valid SSN for each child
        # float investment income (has to be less than 10_300)
        # float earned income/tax liability (tax credit can't exceed tax liability)
        # int age of each child