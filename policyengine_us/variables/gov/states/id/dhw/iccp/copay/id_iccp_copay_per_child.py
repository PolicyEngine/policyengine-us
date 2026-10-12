from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.id.dhw.iccp.id_iccp_time_category import (
    IDICCPTimeCategory,
)


class id_iccp_copay_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Idaho Child Care Program copay per child"
    defined_for = "id_iccp_eligible_child"
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=15",
        "https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=4671&repo=PUBLIC-DOCUMENTS",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.copay
        income = person.spm_unit("id_iccp_countable_income", period)
        family_size = person.spm_unit("spm_unit_size", period.this_year)
        additional_members = max_(family_size - p.max_family_size, 0)
        adjusted_income = max_(
            income - additional_members * p.additional_member_income, 0
        )
        capped_size = clip(family_size, p.min_family_size, p.max_family_size)

        full_time = (
            person("id_iccp_time_category", period) == IDICCPTimeCategory.FULL_TIME
        )
        amount = p.amount
        full_time_amount = select(
            [
                capped_size == 2,
                capped_size == 3,
                capped_size == 4,
                capped_size == 5,
                capped_size == 6,
                capped_size == 7,
            ],
            [
                amount.size_2.full_time.calc(adjusted_income),
                amount.size_3.full_time.calc(adjusted_income),
                amount.size_4.full_time.calc(adjusted_income),
                amount.size_5.full_time.calc(adjusted_income),
                amount.size_6.full_time.calc(adjusted_income),
                amount.size_7.full_time.calc(adjusted_income),
            ],
            default=amount.size_8.full_time.calc(adjusted_income),
        )
        part_time_amount = select(
            [
                capped_size == 2,
                capped_size == 3,
                capped_size == 4,
                capped_size == 5,
                capped_size == 6,
                capped_size == 7,
            ],
            [
                amount.size_2.part_time.calc(adjusted_income),
                amount.size_3.part_time.calc(adjusted_income),
                amount.size_4.part_time.calc(adjusted_income),
                amount.size_5.part_time.calc(adjusted_income),
                amount.size_6.part_time.calc(adjusted_income),
                amount.size_7.part_time.calc(adjusted_income),
            ],
            default=amount.size_8.part_time.calc(adjusted_income),
        )

        in_care = person("childcare_hours_per_week", period.this_year) > 0
        income_amount = where(full_time, full_time_amount, part_time_amount)

        # IDAPA 16.06.12.503 exempts TAFI (Idaho TANF) families and guardians of
        # foster children from the copay. The chart scopes the TAFI exemption to
        # families below 100% FPG; the 503 sub-condition limiting it to TAFI
        # families in non-employment activities is not tracked at the moment.
        tafi = person.spm_unit("is_tanf_enrolled", period)
        fpg = person.spm_unit("spm_unit_fpg", period)
        below_tafi_fpl = income < fpg * p.tafi_exemption_fpl_rate
        tafi_exempt = tafi & below_tafi_fpl
        # IDAPA 16.06.12.503 exempts guardians of foster children at the family
        # level, so any member in foster care exempts all children's copays.
        foster_exempt = add(person.spm_unit, period, ["is_in_foster_care"]) > 0
        # IDAPA 16.06.12.504.01.a sets a flat student copay for post-secondary
        # students working less than 10 hours per week; we don't track weekly
        # work hours at the moment, so the student copay row is not modeled.
        copay = where(tafi_exempt | foster_exempt, 0, income_amount)
        return where(in_care, copay, 0)
