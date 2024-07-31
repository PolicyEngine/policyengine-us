from policyengine_us.model_api import *


class residential_efficiency_electrification_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Residential efficiency and electrification rebate"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.doe.residential_efficiency_electrification_rebate
        expenditures = tax_unit(
            "residential_efficiency_electrification_retrofit_expenditures",
            period,
        )
        savings_kwh = tax_unit(
            "residential_efficiency_electrification_retrofit_energy_savings",
            period,
        )
        current_kwh = tax_unit.household("current_home_energy_use", period)
        # avoid array divide-by-zero warnings by not using where() function
        savings_pct = np.zeros_like(current_kwh)
        mask = current_kwh > 0
        savings_pct[mask] = savings_kwh[mask] / current_kwh[mask]
        income_ami = tax_unit.household("household_income_ami_ratio", period)
        high_cap = p.cap.high.calc(income_ami)
        medium_cap = p.cap.medium.calc(income_ami)
        # Low cap is a dollar amount per given percentage reduction of energy
        # use per dwelling unit for the average home in the state
        average_home_energy_use_in_state = tax_unit.household(
            "average_home_energy_use_in_state", period
        )
        low_cap_per_percent = p.cap.low.calc(income_ami)
        # avoid array divide-by-zero warnings by not using where() function
        reduction = np.zeros_like(average_home_energy_use_in_state)
        mask = average_home_energy_use_in_state > 0
        reduction[mask] = (
            low_cap_per_percent[mask] / average_home_energy_use_in_state[mask]
        )
        low_cap_per_kwh_reduction = 100 * reduction
        low_cap = low_cap_per_kwh_reduction * savings_kwh
        # Uncapped amount is a percent of project costs
        percent = p.percent.calc(income_ami)
        uncapped = percent * expenditures
        cap = select(
            [
                savings_pct >= p.threshold.high,
                savings_pct >= p.threshold.medium,
                savings_pct >= p.threshold.low,
            ],
            [high_cap, medium_cap, low_cap],
            default=0,
        )
        return min_(uncapped, cap)
