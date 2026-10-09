from policyengine_us.model_api import *


class id_qualified_health_insurance_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho health insurance premiums not excluded or deducted elsewhere"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # PDF pages 48-49 (Form 39R, line 18 and its worksheet).
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=48",
    )
    documentation = (
        "Premiums for the taxpayer, spouse, and dependents, before removing "
        "the portion used in Idaho itemized deductions. Reported pretax "
        "premiums are treated as a subset of total reported premiums. "
        "Self-employed premiums already deducted federally are excluded, "
        "including deductions on dependents' own returns."
    )

    def formula(tax_unit, period, parameters):
        premiums = add(tax_unit, period, ["medical_expense_health_insurance_premiums"])
        pretax = add(tax_unit, period, ["pre_tax_health_insurance_premiums"])
        deducted_elsewhere = add(
            tax_unit,
            period,
            [
                "self_employed_health_insurance_ald",
                "dependents_self_employed_health_insurance_ald",
            ],
        )
        return max_(0, premiums - pretax - deducted_elsewhere)
