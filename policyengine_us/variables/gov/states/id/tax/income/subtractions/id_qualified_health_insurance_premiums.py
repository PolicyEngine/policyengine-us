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
        # The deduction's long-term care part (Form 7206 line 2) took no
        # medical insurance premiums, so it does not reduce them.
        # The return's deduction takes the filers' medical parts (Form 7206
        # line 1) before their long-term care parts (line 2), as
        # itemized_medical_expenses_excluded_premiums does, so a supplied
        # deduction below the person amounts takes medical premiums first.
        person = tax_unit.members
        filer = not_(person("is_tax_unit_dependent", period))
        own_deduction = max_(
            0, person("self_employed_health_insurance_ald_person", period)
        )
        own_long_term_care_part = person(
            "self_employed_health_insurance_ald_long_term_care_part", period
        )
        medical_parts = tax_unit.sum((own_deduction - own_long_term_care_part) * filer)
        deduction = max_(0, tax_unit("self_employed_health_insurance_ald", period))
        long_term_care_taken = min_(
            tax_unit.sum(own_long_term_care_part * filer),
            max_(0, deduction - medical_parts),
        )
        deducted_elsewhere = deduction - long_term_care_taken
        return max_(0, premiums - deducted_elsewhere)
