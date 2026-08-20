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
        "models (LA County, the Texas TDHCA service area, seven Texas metro PHAs, "
        "and six Kansas PHA jurisdictions). Each schedule is summed over all tenant-paid "
        "utilities assuming a Multi-Family, all-electric unit. SRO units use the "
        "published SRO row "
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
        # Dallas Housing Authority, apartment/condo/townhouse schedule,
        # effective 2026-01-01.
        "https://dhantx.com/wp-content/uploads/2025/12/HCV-2026-Utility-Allowances-Apt-Townhouse.pdf",
        # El Paso County Housing Authority, apartment schedule, effective 2026.
        "https://epcha.org/hcv-utility-allowances",
        # Tarrant County Housing Assistance Office, multi-family homes,
        # effective 2026-01-01.
        "https://www.tarrantcountytx.gov/content/dam/main/housing-assistance/Documents/TCHAO_Multi-Family%20Homes_Effec.%2001-01-2026.pdf",
        # Housing Authority of the City of Austin, multi-family elevator
        # schedule, effective 2025-06-01.
        "https://www.hacanet.org/wp-content/uploads/2025/03/Utility-Allowance-Schedule-06-01-2025.pdf",
        # Harris County Housing Authority, low-rise apartment schedule,
        # effective 2025-04-01.
        "https://hchatexas.org/wp-content/uploads/HCHA-2025-Utility-Allowance-Chart-Apartments-52667.pdf",
        # Housing Authority of Bexar County, multi-family schedule, effective
        # 2026-01-01.
        "https://habctx.org/wp-content/uploads/2025/06/Multi-Family-UA-2026.pdf",
        # Waco Housing Authority, McLennan County multi-family schedule
        # (Schedule MC3), effective 2025-10-01.
        "https://www.wacopha.org/page/open/2202/0/mclennan%20MF.pdf",
        # Wichita Housing Authority (Sedgwick County), effective 2025-07-01.
        "https://www.wichita.gov/DocumentCenter/View/31965/2025-Utility-Allowances",
        # Wichita Housing Authority (Sedgwick and Butler Counties; Harvey
        # County except the City of Newton), effective 2026.
        "https://www.wichita.gov/DocumentCenter/View/37084/2026-Utility-Allowances-PDF",
        # Topeka Housing Authority (Shawnee County), effective 2025.
        "https://www.tha.gov/wp-content/uploads/2025/04/All-Utility-Allowances.pdf",
        # Kansas City Kansas Housing Authority (Wyandotte County), 2026.
        "https://www.kckha.org/Documents/Housing/HCV/2026%20Utility%20Schedules-Kansas%20City%20KS-HUD%2052667-2026%20(0-5%20BR).pdf",
        # Johnson County Housing Authority (Johnson County), effective 2026-03-01.
        "https://www.jocogov.org/sites/default/files/files/2026-03/2026%20Utility%20Allowances-R.pdf",
        # Manhattan Housing Authority (Riley County), large apartment schedule,
        # effective 2024-11-20, with its water/sewer attachment.
        "https://www.mhaks.com/212/Utility-Allowances",
        # Lawrence-Douglas County Housing Authority, high-rise/apartment
        # schedule adopted for the 2025 voucher program.
        "https://storage.googleapis.com/wzukusers/user-31752601/documents/15086e89c84648f5bb744ea2e2fddd8c/September%2023%202024%20Board%20Meeting.pdf",
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
