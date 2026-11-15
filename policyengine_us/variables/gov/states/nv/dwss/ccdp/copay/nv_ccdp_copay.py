from policyengine_us.model_api import *


class nv_ccdp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Nevada CCDP monthly family co-payment"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = (
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/CC_PT_06-25_ANNUAL_INCOME_CHANGES_10.02.2025.pdf#page=1",
        "https://dwss.nv.gov/uploadedFiles/dwssnvgov/content/Care/CC%20PT%2007-23%20Annual%20Income%20Ceiling%20Increase%20(Public%20Distribution).pdf#page=2",
        "https://nevadachildcare.netlify.app/static/200a0b5ae99f788e8c99d6f7824dc92b/Child-Care-Updates-Parents-.pdf#page=1",
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=75",
    )

    def formula(spm_unit, period, parameters):
        # Nevada's copayment has followed three dated rules:
        # - July 1, 2022 through March 31, 2024: American Rescue Plan funds covered
        #   every family's copayment.
        # - April 1 through September 30, 2024: a percent of gross income, 0% to 7%,
        #   from the chart effective October 1, 2023, by household size and income.
        #   Households above fourteen people use the fourteen-person column.
        # - From October 1, 2024: a flat monthly amount by income as a share of SMI
        #   (State Plan Section 2.4.v): up to 33% SMI -> $0; up to 42% SMI -> $90;
        #   above 42% -> $150, with each band top rounded to the nearest dollar as the
        #   charts print it. The flat schedule also stands in for dates before July
        #   2022.
        ccdp = parameters(period).gov.states.nv.dwss.ccdp
        p = ccdp.copay
        if p.reimbursed:
            return spm_unit.empty_array()
        # MS 316 rounds monthly income to the nearest dollar before reading the
        # chart. Countable income floors at zero, so negative self-employment
        # income can't produce a negative copayment.
        monthly_income = spm_unit("nv_ccdp_monthly_countable_income", period)
        if p.percent_of_income.in_effect:
            size = spm_unit("spm_unit_size", period.this_year)
            scales = p.percent_of_income
            sizes = range(1, 14)
            share = select(
                [size == n for n in sizes],
                [scales[f"size_{n}"].calc(monthly_income) for n in sizes],
                default=scales.size_14.calc(monthly_income),
            )
            copay = share * monthly_income
        else:
            # Each threshold of the flat schedule gives, as a share of SMI, the top
            # of the band below it. The charts from October 2024 print each top as
            # the nearest dollar, and income above a top pays the next band.
            monthly_smi = spm_unit("nv_ccdp_smi", period)
            scale = p.amount
            copay = np.full_like(monthly_income, scale.amounts[0])
            for threshold, amount in zip(scale.thresholds[1:], scale.amounts[1:]):
                band_top = monthly_smi * threshold
                if ccdp.chart_rounds_to_nearest_dollar:
                    band_top = np.floor(np.round(band_top, 2) + 0.5)
                copay = where(monthly_income > band_top, amount, copay)
        # Manual MS 180/181 (Co-Payments) waives the copay for exactly three
        # categories: TANF/NEON referrals, CPS/foster placements, and homeless
        # households (plus a discretionary case-by-case waiver by the CCDP
        # Chief). Use is_tanf_enrolled for the NEON waiver to avoid the
        # CCDP <-> TANF circular dependency. Waivers apply at the whole-family
        # level; we don't track per-child copay waivers at the moment.
        # State Plan Section 3.3.1 also checks boxes to waive copays for families
        # with children with disabilities and for Head Start / Early Head Start,
        # but those are "broad flexibility" plan options the operative Manual
        # MS 180/181 does not adopt as automatic exemptions (and the State Plan's
        # Head Start waiver is specifically for wraparound-collaboration cases,
        # not all enrollees). We follow the operative Manual list and do not
        # model the disability or Head Start waivers at the moment.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        is_eligible_child = person("nv_ccdp_eligible_child", period)
        in_protective_care = is_eligible_child & (
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        has_protective_child = spm_unit.any(in_protective_care)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        waived = is_tanf_enrolled | has_protective_child | is_homeless
        return where(waived, 0, copay)
