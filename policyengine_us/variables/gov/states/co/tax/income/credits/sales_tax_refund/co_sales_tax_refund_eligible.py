from policyengine_us.model_api import *


class co_sales_tax_refund_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado sales tax refund"
    definition_period = YEAR
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23"
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        # The tax unit is eligible when at least one filer (head or spouse) is a
        # qualified individual. Using the person-level test as the single source
        # of truth keeps this gate consistent with the per-person refund amount,
        # which counts only head/spouse rather than any member's earnings.
        return add(tax_unit, period, ["co_sales_tax_refund_person_eligible"]) > 0
