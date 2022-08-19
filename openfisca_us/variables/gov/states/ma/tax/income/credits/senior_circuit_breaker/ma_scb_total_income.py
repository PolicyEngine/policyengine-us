from openfisca_us.model_api import *


class ma_scb_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total income for the MA Senior Circuit Breaker"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # Part (k)
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        ma_gross_income = tax_unit(
            "ma_gross_income", period
        )  # The law specifies to start at AGI and re-add deducted capital losses. We instead start from gross income, on an equivalent path.
        scb = parameters(
            period
        ).gov.states.ma.tax.income.credits.senior_circuit_breaker
        disallowed_deductions = add(
            tax_unit, period, scb.income.disallowed_deductions
        )

        # Re-add some exemptions
        person = tax_unit.members
        tax = parameters(period).gov.states.ma.tax.income
        blind = person("is_blind", period)
        dependent = person("is_tax_unit_dependent", period)
        count_blind = tax_unit.sum(~dependent & blind)
        blind_exemption = tax.exemptions.blind * count_blind
        # (1C) and (2C): Aged exemptions.
        age = person("age", period)
        count_aged = tax_unit.sum(
            ~dependent & (age >= tax.exemptions.aged.age)
        )
        aged_exemption = tax.exemptions.aged.amount * count_aged
        # (3): Dependent exemptions.
        count_dependents = tax_unit("tax_unit_dependents", period)
        dependent_exemption = tax.exemptions.dependent * count_dependents
        exemptions = blind_exemption + aged_exemption + dependent_exemption

        return max_(0, ma_gross_income + disallowed_deductions - exemptions)
