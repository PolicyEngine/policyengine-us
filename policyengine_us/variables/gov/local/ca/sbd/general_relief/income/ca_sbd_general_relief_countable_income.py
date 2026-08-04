from policyengine_us.model_api import *


class ca_sbd_general_relief_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Bernardino County General Relief countable income"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/b2fb756f-da07-452e-bdba-e3c4eda464c5.doc",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.income
        person = spm_unit.members
        # "All income in the AU must be taken into consideration": a member
        # barred for SSI/SSP, CAPI, or CalWORKs receipt is supported by the
        # other program's budget and is not part of the AU, so neither
        # their benefit check nor their other income is charged to the AU
        # (mirroring how CalWORKs treats SSI recipients). Members excluded
        # for other reasons (immigration status, linkage) remain family
        # members whose income supports the AU, so their income counts.
        # Actual cash contributions a barred member hands the AU would
        # count under the county's cash-contributions row, but no input
        # distinguishes them.
        counted = ~person(
            "ca_sbd_general_relief_receives_other_cash_assistance", period
        )
        earned = spm_unit.sum(
            person("ca_sbd_general_relief_gross_earned_income", period) * counted
        )
        # The first $10 and 20% of the balance are exempt per assistance
        # unit, applied after summing earned income to the unit. The floor
        # also keeps self-employment losses from offsetting unearned income.
        countable_earned = max_(earned - p.earned_exemption.flat, 0) * (
            1 - p.earned_exemption.rate
        )
        # Unearned income counts in full, with no exemptions or deductions.
        unearned = spm_unit.sum(
            person("ca_sbd_general_relief_gross_unearned_income", period) * counted
        )
        return countable_earned + unearned
