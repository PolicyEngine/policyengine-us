from policyengine_us.model_api import *


class me_heap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Maine HEAP regular heating benefit"
    defined_for = "me_heap_eligible"
    reference = (
        # PDF pages 15-17
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=15",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
        # PDF pages 1-2
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ME_BenefitMatrix_2026.pdf#page=1",
        # PDF pages 5, 10
        "https://liheapch.acf.gov/docs/2026/state-plans/ME_Plan_2026.pdf#page=5",
        "https://liheapch.acf.gov/docs/2025/state-plans/ME_Plan_2025.pdf#page=8",
    )
    documentation = (
        "Annual HEAP Fuel Assistance benefit: points for dwelling, county, fuel, "
        "priority and subsidized housing (plus base points from June 29, 2026), "
        "adjusted by the income multiplier, prorated for ineligible members, "
        "rounded up and multiplied by the dollar value per point; subsidized "
        "tenants with heat in rent receive the nominal benefit. The $22 value "
        "per point is an estimate because MaineHousing has not announced one. "
        "The TANF Fuel Supplemental Benefit, ECIP crisis assistance, "
        "weatherization and CHIP are excluded. Pellet, corn, bio-fuel and "
        "biobrick rows have no heating_type value, and WOOD uses the cordwood "
        "row. Eligibility requires a heating bill or heat included in rent. "
        "SOLAR uses the electricity row, as for a grid-tied home with electric "
        "heat (heating_expense's assumption); an off-grid solar-only home has "
        "no electricity bill, so no energy cost for heat. Roomers, "
        "live-in attendants, the optional exclusion of college students and the "
        "residency tests have no inputs. Verified for model years 2026 and "
        "2027; earlier years are unverified backfill."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.me.msha.heap.payment
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        points = spm_unit("me_heap_points", period)
        return where(
            heat_in_rent & subsidized,
            p.nominal_benefit,
            points * p.value_per_point,
        )
