from policyengine_us.model_api import *


class me_property_tax_fairness_credit(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = "me_property_tax_fairness_credit_eligible"

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        utilities_included_in_rent = tax_unit(
            "utilities_included_in_rent", period
        )
        utility_expenses = add(tax_unit, period, ["utility_expense"])
        # A separate calcuation exists for the case where utilities are included in rent
        # if the filer does not know the portion of rent that is attributable to utilities
        # This is not implemented
        applicable_rent_amount = where(
            utilities_included_in_rent,
            rent - utility_expenses,
            rent,
        )
        applicable_rent = applicable_rent_amount * p.rate.rent
        rent_and_property_tax = applicable_rent + ptax
        filing_status = tax_unit("filing_status", period)
        dependents = tax_unit("ctc_qualifying_children", period)
        capped_dependents = min_(dependents, 2)
        benefit_base = p.amount[filing_status][capped_dependents]
        capped_benefit_base = min_(benefit_base, rent_and_property_tax)
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        income_rate = income * p.rate.income
        uncapped_credit = max_(capped_benefit_base - income_rate, 0)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)

        head_cap = p.cap.calc(age_head)
        spouse_cap = p.cap.calc(age_spouse)

        cap = max_(head_cap, spouse_cap)

        base_credit = min_(uncapped_credit, cap)

        if not p.veterants_in_effect:
            return min_(rent_and_property_tax, base_credit)
        else:
            # compute permanently and totally disabled veterans's credit
            person = tax_unit.members
            disabled_service_connected_veteran = person(
                "is_fully_disabled_service_connected_veteran", period
            )
            permanently_disabled_veteran = person(
                "is_permanently_disabled_veteran", period
            )
            qualified_disabled_veteran_present = tax_unit.any(
                disabled_service_connected_veteran
                | permanently_disabled_veteran
            )

            qualified_veterans_credit = (
                base_credit * p.veterants_credit_multiply_factor
            )
            qualified_veterans_credit_final = where(
                qualified_disabled_veteran_present,
                qualified_veterans_credit,
                base_credit,
            )
            return min_(rent_and_property_tax, qualified_veterans_credit_final)
