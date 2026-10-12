from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.utility_allowance import (
    MAX_BEDROOMS,
    SRO_BEDROOMS,
    utility_allowance_schedule,
)


class hud_utility_allowance(Variable):
    value_type = float
    entity = Household
    label = "HUD utility allowance"
    unit = USD
    documentation = (
        "Monthly utility allowance for HUD programs, annualized. Set per public "
        "housing agency by bedroom size; encoded for the counties PolicyEngine "
        "models (LA County, the Texas TDHCA service area, and four Kansas PHAs). "
        "Each schedule is summed over all tenant-paid utilities assuming a "
        "Multi-Family, all-electric unit. SRO units use the published SRO row "
        "where one exists, otherwise 75% of the zero-bedroom value per 24 CFR "
        "982.604(b). Returns 0 for counties without an encoded schedule."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/24/982.517",
        # SRO allowance = 75% of the zero-bedroom allowance.
        "https://www.law.cornell.edu/cfr/text/24/982.604",
        # LA County (LACDA), effective 2025-07-01. The 2023-vintage values came
        # from LACDA's prior schedule (utility-allownce-2022.pdf, "as of
        # 2023-07-01"), which is no longer online.
        "https://www.lacda.org/docs/librariesprovider25/shared-content---documents/utility-allowance/lacda-utility-allowance-schedule-7-1-2025.pdf",
        # Texas (TDHCA service area), effective 2026-01-01.
        "https://www.tdhca.texas.gov/section-8-resources",
        # Wichita Housing Authority (Sedgwick County), effective 2025-07-01.
        "https://www.wichita.gov/DocumentCenter/View/31965/2025-Utility-Allowances",
        # Topeka Housing Authority (Shawnee County), effective 2025.
        "https://www.tha.gov/wp-content/uploads/2025/04/All-Utility-Allowances.pdf",
        # Kansas City Kansas Housing Authority (Wyandotte County), 2026.
        "https://www.kckha.org/Documents/Housing/HCV/2026%20Utility%20Schedules-Kansas%20City%20KS-HUD%2052667-2026%20(0-5%20BR).pdf",
        # Johnson County Housing Authority (Johnson County), effective 2026-03-01.
        "https://www.jocogov.org/sites/default/files/files/2026-03/2026%20Utility%20Allowances-R.pdf",
    )
    defined_for = "tenant_pays_utilities"

    def formula(household, period, parameters):
        # Key on county_fips, matching hud_fair_market_rent (the fallback
        # payment standard) so both HUD dollar amounts resolve off the same
        # geography signal. county_fips is populated for every household in the
        # microdata (unlike the county enum, which is not stored and would
        # decode to the first-in-state county), so this is the reliable key in
        # both the household and microsimulation paths.
        county_fips = household("county_fips", period)
        bedrooms = household("bedrooms", period)
        is_sro = household("is_sro", period)
        # SRO units use a dedicated schedule row; other units clip to the
        # published bedroom range (larger units reuse the top bedroom value).
        lookup_bedrooms = where(
            is_sro,
            SRO_BEDROOMS,
            np.clip(bedrooms.astype(int), 0, MAX_BEDROOMS),
        )
        schedule = utility_allowance_schedule(period.start.year)
        df = pd.DataFrame(
            {
                "county_fips": pd.Series(county_fips).astype(str).str.zfill(5),
                "bedrooms": lookup_bedrooms,
            }
        )
        # validate="many_to_one": many households may share one schedule row,
        # but the schedule must be unique per (county_fips, bedrooms). Fails
        # loudly if a future CSV ever duplicates a merge key.
        matched = df.merge(
            schedule,
            on=["county_fips", "bedrooms"],
            how="left",
            validate="many_to_one",
        )
        monthly = matched["monthly_value"].fillna(0).to_numpy()
        # SRO units in counties without a published SRO row take a share of the
        # zero-bedroom allowance (75% per 24 CFR 982.604(b)), applied here as a
        # reform-visible parameter rather than baked into the schedule.
        sro_share = parameters(
            period
        ).gov.hud.utility_allowance.sro_share_of_zero_bedroom
        uses_share = (
            matched["sro_uses_zero_bedroom_share"].fillna(False).astype(bool).to_numpy()
        )
        monthly = where(uses_share, monthly * sro_share, monthly)
        return monthly * MONTHS_IN_YEAR
