from policyengine_us.model_api import *


class id_receives_aged_or_disabled_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer receives the Idaho aged or disabled credit over the deduction"
    definition_period = YEAR
    # 63-3025D(1) indicates that filers can only take either the deduction or credit.
    reference = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3025d/"
    defined_for = StateCode.ID
    default_value = True

    def formula(tax_unit, period, parameters):
        tax_if_credit = tax_unit(
            "id_income_tax_if_receiving_aged_or_disabled_credit", period
        )
        tax_if_deduction = tax_unit(
            "id_income_tax_if_receiving_aged_or_disabled_deduction", period
        )
        # id_income_tax is a liability net of refundable credits, so the more
        # beneficial option yields lower Idaho income tax. Ties keep the credit,
        # preserving the prior default.
        return tax_if_credit <= tax_if_deduction
