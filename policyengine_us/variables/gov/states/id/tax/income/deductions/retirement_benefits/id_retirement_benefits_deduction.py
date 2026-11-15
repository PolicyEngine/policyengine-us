from policyengine_us.model_api import *


class id_retirement_benefits_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho retirement benefits deduction"
    unit = USD
    reference = [
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00088/EFO00088_03-01-2023.pdf",
    ]
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.deductions.retirement_benefits
        filing_status = tax_unit("filing_status", period)
        # Line 8a
        # Max retirement benefits deduction amount
        cap = p.cap[filing_status]
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Line 8b
        # Railroad Retirement Act benefits received, taxable or not:
        # Form RRB-1099 box 5 plus Form RRB-1099-R box 7 (63-3022A(3)).
        railroad_benefits = add(
            person,
            period,
            [
                "railroad_social_security_equivalent_benefits",
                "taxable_railroad_pension_benefits",
                "tax_exempt_railroad_pension_benefits",
            ],
        )
        # Line 8c
        # Social Security retirement benefits received
        ss_retirement = person("social_security_retirement", period)
        total_federal_benefits = tax_unit.sum(
            (railroad_benefits + ss_retirement) * head_or_spouse
        )
        # Line 8d
        # Base amount minus lines 8b and 8c
        ded_amt = max_(cap - total_federal_benefits, 0)
        # Line 8e
        # Qualified retirement benefits included in federal income
        # The head or spouse condition is included in the eligible person variable
        relevant_income = add(
            tax_unit,
            period,
            ["id_retirement_benefits_deduction_relevant_income"],
        )
        # Line 8f
        return min_(ded_amt, relevant_income)
