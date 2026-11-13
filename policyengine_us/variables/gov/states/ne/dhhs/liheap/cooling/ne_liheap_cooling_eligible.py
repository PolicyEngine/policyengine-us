from policyengine_us.model_api import *


class ne_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP regular cooling assistance eligibility"
    defined_for = StateCode.NE
    reference = (
        # PDF pages 1-3
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%202%20(06-26-2022).pdf/1747#page=1",
        # 476 NAC 3-002.02
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%203%20(12-26-2020).pdf/1748#page=1",
        # PDF pages 9,11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/NE_Plan_2026.pdf#page=9",
        "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap.cooling
        person = spm_unit.members
        age = person("age", period)
        # 476 NAC 2-002.02 excludes members who fail the citizenship and
        # residency rules, so they cannot be the qualifying member.
        included = person("is_snap_immigration_status_eligible", period.first_month)
        # 2-003(A) requires a child under 6 who receives ADC. ADC receipt is
        # known only for the whole unit, so a child under 6 in a unit that
        # receives ADC qualifies even if that child is outside the grant.
        receives_adc = spm_unit("tanf", period) > 0
        # 476 NAC 2-003(A) and (B). Routes (C), a severe illness aggravated by
        # extreme heat verified on form IM-55, and (D), an air conditioner from
        # the Department within four years, have no existing inputs, so
        # households qualifying only through them are not paid. Disability is
        # not one of the 2-003 routes.
        young_child = spm_unit.any(included & (age < p.adc_child_age_limit))
        adc_child = young_child & receives_adc
        elderly_member = spm_unit.any(included & (age >= p.elderly_age))
        # FY2026 plan section 3.3 requires subsidized households and renters
        # with utilities in rent to be "responsible for a portion of the
        # cooling utilities", the sentence section 2.3 sets for heating. It is
        # read as ne_liheap_eligible reads section 2.3: an unsubsidized renter
        # with utilities in the rent is responsible, since 476 NAC 3-002.02
        # lets the Department pay a household directly "if utilities are
        # included in rent" for every 3-001 payment type, cooling included. A
        # household receiving housing assistance or living in public housing
        # needs a cooling cost of its own.
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        utilities_in_rent = ~spm_unit.household("tenant_pays_utilities", period) & (
            add(spm_unit, period, ["rent"]) > 0
        )
        # A cooling cost apart from rent (has_cooling_expense) is a PolicyEngine
        # convention of the all-state cooling work; 476 NAC 2-003 names no air
        # conditioner or separate cooling cost.
        responsible = spm_unit("has_cooling_expense", period) | (
            utilities_in_rent & ~subsidized
        )
        # The cooling table has no fuel column, so heating_type is not read.
        return (
            spm_unit("ne_liheap_income_eligible", period)
            & responsible
            & (adc_child | elderly_member)
        )
