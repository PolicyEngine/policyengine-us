from policyengine_us.model_api import *


def create_ny_s04487_newborn_credit() -> Reform:
    """
    NY Senate Bill S04487 - Supplemental Empire State Child Tax Credit for Newborns

    Establishes a $1,000 supplemental credit for newborns (children born in
    the current or previous tax year who have not been previously claimed).

    Reference: https://www.nysenate.gov/legislation/bills/2025/S4487
    """

    class ny_s04487_qualifying_newborn(Variable):
        value_type = bool
        entity = Person
        label = "Qualifies as newborn for NY S04487 credit"
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/bills/2025/S4487"
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.ny.s04487
            in_effect = p.in_effect
            # Child must be age 0 or 1 (born in current or previous tax year)
            age = person("age", period)
            age_eligible = age <= p.max_age
            # Must be a dependent
            is_dependent = person("is_tax_unit_dependent", period)
            return in_effect & age_eligible & is_dependent

    class ny_s04487_newborn_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Number of qualifying newborns for NY S04487 credit"
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/bills/2025/S4487"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            qualifying = person("ny_s04487_qualifying_newborn", period)
            return tax_unit.sum(qualifying)

    class ny_s04487_newborn_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY S04487 supplemental newborn credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/bills/2025/S4487"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.s04487
            in_effect = p.in_effect
            newborn_count = tax_unit("ny_s04487_newborn_count", period)
            credit_per_newborn = p.amount
            return where(in_effect, newborn_count * credit_per_newborn, 0)

    class ny_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ny.tax.income.credits
            standard_credits = add(tax_unit, period, p.refundable)
            # Add newborn credit from S04487
            newborn_credit = tax_unit("ny_s04487_newborn_credit", period)
            return standard_credits + newborn_credit

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_s04487_qualifying_newborn)
            self.update_variable(ny_s04487_newborn_count)
            self.update_variable(ny_s04487_newborn_credit)
            self.update_variable(ny_refundable_credits)

    return reform


def create_ny_s04487_newborn_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_s04487_newborn_credit()

    p = parameters(period).gov.contrib.states.ny.s04487

    if p.in_effect:
        return create_ny_s04487_newborn_credit()
    else:
        return None


ny_s04487_newborn_credit = create_ny_s04487_newborn_credit_reform(
    None, None, bypass=True
)
