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
        "Premiums paid by the taxpayer and spouse for themselves and their "
        "dependents, before removing the portion used in Idaho itemized "
        "deductions. The premium inputs exclude premiums paid through "
        "pretax payroll deductions. Those premiums are reported separately "
        "in pre_tax_health_insurance_premiums, which never enters this "
        "subtraction. "
        "Self-employed premiums already deducted on the filers' federal "
        "return are excluded. Dependents' own payments are excluded "
        "regardless of their federal deduction."
    )

    def formula(tax_unit, period, parameters):
        premiums = tax_unit_non_dep_add(
            tax_unit, period, ["medical_expense_health_insurance_premiums"]
        )
        # Dependents' federal deductions concern their excluded payments,
        # so they must not reduce the filers' qualifying premiums again.
        deducted_elsewhere = tax_unit("self_employed_health_insurance_ald", period)
        return max_(0, premiums - deducted_elsewhere)
