from policyengine_us.model_api import *


class ok_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OK itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK
    """
    NOTE: OK itemization requires federal itemization
    NOTE: no loss deductions allowed
    NOTE: property tax deductions limited by federal rules
    NOTE: limited to $17K with exceptions for medical and charity

    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        federal_itm_deds_less_salt = add(tax_unit, period, itm_deds)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return federal_itm_deds_less_salt + uncapped_property_taxes
    """
