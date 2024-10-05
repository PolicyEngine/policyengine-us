from policyengine_us.model_api import *


class id_receives_aged_or_disabled_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Filer receives the Idaho aged or disabled credit over the deduction"
    )
    definition_period = YEAR
    # 63-3025D(1) indicates that filers can only take either the deduction or credit.
    reference = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3025d/"
    defined_for = StateCode.ID
    default_value = True
