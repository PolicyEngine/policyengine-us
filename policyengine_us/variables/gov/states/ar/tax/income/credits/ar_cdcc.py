from policyengine_us.model_api import *


class ar_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas Child Care Expenses Credit"
    unit = USD
    documentation = "https://casetext.com/regulation/arkansas-administrative-code/agency-006-department-of-finance-and-administration/division-05-division-of-revenues/regulation-1997-4-comprehensive-individual-income-tax-regulations/rule-26-51-502-household-and-dependent-care-services"
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.credits.cdcc
        agi = tax_unit("adjusted_gross_income", period)

        # 1. get cdcc expenses
        # check disabled child numbers, only calculate healthy child here
        children = tax_unit("tax_unit_children", period)
        person = tax_unit.members
        disabled = person("is_disabled", period)
        health_children = children - tax_unit.sum(disabled)
        tax_unit_childcare_expenses = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        total_expenses = tax_unit_childcare_expenses * health_children
        earned_income = tax_unit("min_head_spouse_earned", period)
        capped_expenses = min_(earned_income, total_expenses)
        max_amounts = p.max_amount.calc(health_children)
        cdcc_expenses = min(max_amounts, capped_expenses)

        # 2. get corresponding decimal amount based on agi
        decimal_amt = p.decimal_amount_to_agi.calc(agi)

        # 3. get cdcc
        cdcc = decimal_amt * cdcc_expenses 
        # ??? rate how to use the 10% 
        rate = p.rate.additional_facility

        # 4. add disabled cdcc credits
        disabled_children = tax_unit.sum(disabled)
        disabled_addons = disabled_children * p.disabled_amount

        return cdcc * rate + disabled_addons

