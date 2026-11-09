from policyengine_us.model_api import *


class ne_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP regular cooling assistance eligibility"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%202%20(06-26-2022).pdf/1747#page=2",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/NE_Plan_2026.pdf#page=11",
        "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap.cooling
        person = spm_unit.members
        age = person("age", period)
        # 476 NAC 2-002.02 excludes members who fail the citizenship and
        # residency rules, so they cannot be the qualifying member.
        included = person("is_snap_immigration_status_eligible", period.first_month)
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
        # cooling utilities"; the cooling cost input stands for that
        # responsibility. Cooling paid only through rent has no existing input.
        has_cooling_expense = spm_unit("has_cooling_expense", period)
        # The heating fuel must be reported: UNSPECIFIED pays nothing, while
        # NONE and every known fuel qualify, since the cooling table has no
        # fuel column.
        heating_type = spm_unit("heating_type", period)
        fuel_reported = heating_type != heating_type.possible_values.UNSPECIFIED
        return (
            spm_unit("ne_liheap_income_eligible", period)
            & has_cooling_expense
            & fuel_reported
            & (adc_child | elderly_member)
        )
