from openfisca_us.model_api import *


class pa_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA Use Tax"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=22"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        income = tax_unit("pa_total_taxable_income", period)
        # Parameters vary depending on whether filer is in
        # - Philadelphia (county==city)
        # - Allegheny County
        # - Rest of PA
<<<<<<< HEAD
        county = tax_unit.household("county", period)
        counties = county.possible_values
        philadelphia = county == counties.PHILADELPHIA_COUNTY_PA
        allegheny = county == counties.ALLEGHENY_COUNTY_PA
        rest_of_pa = ~(philadelphia | allegheny)
        geo_list = [philadelphia, allegheny, rest_of_pa]
=======
        county = tax_unit.household("county_str", period)
        # counties = county.possible_values

        philadelphia = county == "PHILADELPHIA_COUNTY_PA"
        allegheny = county == "ALLEGHENY_COUNTY_PA"
        geo_list = [philadelphia, allegheny]
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
        p = parameters(period).gov.states.pa.tax.use_tax
        # Compute main amount.
        main_amount = select(
            geo_list,
<<<<<<< HEAD
            [p.main.philadelphia.calc(income), p.main.allegheny.calc(income), p.main.rest_of_pa.calc(income)]
        )
        # Compute the uncapped amount based on the higher threshold.
        excess_over_higher_threshold = max_(income - p.higher.threshold, 0)
        higher_rate = select(geo_list, [p.higher.rate.philadelphia, p.higher.rate.allegheny, p.higher.rate.rest_of_pa])
        uncapped_higher_amount = excess_over_higher_threshold * higher_rate
        # Cap that amount.
        higher_cap = select(geo_list, [p.higher.cap.philadelphia, p.higher.cap.allegheny, p.higher.cap.rest_of_pa])
=======
            [
                p.main.philadelphia_county.calc(income),
                p.main.allegheny_county.calc(income),
            ],
            p.main.rest_of_pa.calc(income),
        )
        # Compute the uncapped amount based on the higher threshold.
        excess_over_higher_threshold = max_(income - p.higher.threshold, 0)
        higher_rate = select(
            geo_list,
            [
                p.higher.rate.philadelphia_county,
                p.higher.rate.allegheny_county,
            ],
            p.higher.rate.rest_of_pa,
        )
        uncapped_higher_amount = excess_over_higher_threshold * higher_rate
        # Cap that amount.
        higher_cap = select(
            geo_list,
            [p.higher.cap.philadelphia_county, p.higher.cap.allegheny_county],
            p.higher.cap.rest_of_pa,
        )
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
        higher_amount = min_(uncapped_higher_amount, higher_cap)
        # Return main or higher amount depending on if income exceeds the higher threshold.
        return main_amount + higher_amount
