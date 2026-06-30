from policyengine_us.model_api import *


FIRST_CPI_U_YEAR = 1913


def capital_gains_indexation_price_level(parameters, year, transition_year):
    if year <= transition_year:
        return parameters(f"{year}-01-01").gov.bls.cpi.cpi_u

    cpi_u_transition = parameters(f"{transition_year}-01-01").gov.bls.cpi.cpi_u
    chained_cpi_transition = parameters(f"{transition_year}-01-01").gov.bls.cpi.c_cpi_u
    chained_cpi_year = parameters(f"{year}-01-01").gov.bls.cpi.c_cpi_u
    return cpi_u_transition * chained_cpi_year / chained_cpi_transition


class tax_unit_long_term_capital_gains_indexation_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "tax unit long-term capital gains basis indexation adjustment"
    unit = USD
    documentation = (
        "Reduction in taxable long-term capital gains from indexing basis to inflation."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.capital_gains.indexation
        if not p.applies:
            return np.zeros(tax_unit.count)

        person = tax_unit.members
        year = period.start.year
        gains = add(tax_unit, period, ["long_term_capital_gains_before_response"])
        basis = add(tax_unit, period, ["long_term_capital_gains_basis"])

        person_gains = person("long_term_capital_gains_before_response", period)
        person_years_held = person("long_term_capital_gains_years_held", period)
        person_weights = abs(person_gains)
        weight_sum = tax_unit.sum(person_weights)
        weighted_years_held = tax_unit.sum(person_years_held * person_weights)
        years_held = np.divide(
            weighted_years_held,
            weight_sum,
            out=np.zeros_like(weighted_years_held),
            where=weight_sum != 0,
        )

        rounded_years_held = np.rint(np.nan_to_num(years_held)).astype(int)
        acquisition_year = year - rounded_years_held

        transition_year = p.chained_cpi_transition_year
        current_price_level = capital_gains_indexation_price_level(
            parameters, year, transition_year
        )
        indexation_ratio = np.ones(tax_unit.count)
        for purchase_year in np.unique(acquisition_year):
            if purchase_year < FIRST_CPI_U_YEAR or purchase_year > year:
                continue
            purchase_price_level = capital_gains_indexation_price_level(
                parameters, int(purchase_year), transition_year
            )
            indexation_ratio = where(
                acquisition_year == purchase_year,
                current_price_level / purchase_price_level,
                indexation_ratio,
            )

        eligible = (
            (basis > 0)
            & (years_held > p.minimum_holding_period)
            & (acquisition_year > p.purchase_year_threshold)
        )
        adjustment = basis * max_(0, indexation_ratio - 1)

        if p.cap_adjustment_to_gain:
            adjustment = where(gains > 0, min_(adjustment, gains), 0)

        return where(eligible, adjustment, 0)
