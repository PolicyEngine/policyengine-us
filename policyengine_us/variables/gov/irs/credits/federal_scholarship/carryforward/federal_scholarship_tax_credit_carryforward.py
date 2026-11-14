from policyengine_us.model_api import *


def _available_carryforward(tax_unit, period, parameters, ages):
    p = parameters(period).gov.irs.credits.federal_scholarship
    available = np.zeros(tax_unit.count)
    if not p.in_effect:
        return available
    for age in ages:
        origin = parameters(
            period.offset(-age, "year")
        ).gov.irs.credits.federal_scholarship
        if age <= p.carryforward_years and origin.in_effect:
            available += max_(
                tax_unit(f"federal_scholarship_tax_credit_carryforward_{age}", period),
                0,
            )
    return available


def _remaining_carryforward(tax_unit, period, parameters, age):
    p = parameters(period).gov.irs.credits.federal_scholarship
    vintage = _available_carryforward(tax_unit, period, parameters, [age])
    older = _available_carryforward(
        tax_unit, period, parameters, range(age + 1, p.carryforward_years + 1)
    )
    used = max_(tax_unit("federal_scholarship_tax_credit", period) - older, 0)
    return max_(vintage - used, 0)


class federal_scholarship_tax_credit_carryforward(Variable):
    value_type = float
    entity = TaxUnit
    label = "Available Federal Scholarship Tax Credit carryforward"
    unit = USD
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.federal_scholarship
        return _available_carryforward(
            tax_unit, period, parameters, range(1, p.carryforward_years + 1)
        )
