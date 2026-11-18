from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    aca_rating_areas,
    aca_rating_area_corrections,
)


class slcsp_rating_area_default(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area outside of LA County"
    definition_period = YEAR
    reference = "https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/state-gra"
    documentation = (
        "The county's ACA rating area: aca_rating_areas.csv, with the counties in "
        "aca_rating_area_corrections.csv moved to CMS's rating area from their "
        "start_year. Counties not in either file fall in rating area 1."
    )

    def formula(household, period, parameters):
        county_str = household("county_str", period)

        # Corrections in effect this year replace the base map's rows.
        corrections = aca_rating_area_corrections[
            aca_rating_area_corrections["start_year"] <= period.start.year
        ]
        corrections = corrections.sort_values("start_year").drop_duplicates(
            "county", keep="last"
        )
        mapping = pd.concat(
            [
                aca_rating_areas[
                    ~aca_rating_areas["county"].isin(corrections["county"])
                ],
                corrections[["county", "rating_area"]],
            ]
        )

        df_matched = pd.merge(
            pd.DataFrame({"county": county_str}),
            mapping,
            how="left",
            on="county",
        )
        return df_matched["rating_area"].fillna(1).astype(int).values
