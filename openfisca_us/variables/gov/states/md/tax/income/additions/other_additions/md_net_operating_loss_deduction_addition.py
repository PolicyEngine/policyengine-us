## md_net_operating_loss_deduction_addition.py
from openfisca_us.model_api import *

class md_net_operating_loss_deduction_addition(Variable):
    # h. Net operating loss deduction to the extent of a double benefit. See Administrative Release 18 at www.marylandtaxes.gov.
    value_type = float
    entity = TaxUnit
    label = "MD Net Operating Loss Deduction"
    documentation = "Net operating loss deduction to the extent of a double benefit. See Administrative Release 18 at www.marylandtaxes.gov."
    unit = USD
    definition_period = YEAR