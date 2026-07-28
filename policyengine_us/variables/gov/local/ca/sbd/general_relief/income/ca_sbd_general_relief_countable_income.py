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
        # All income in the assistance unit is taken into consideration,
        # including income (and SSI) of members barred from the unit for
        # other-cash-assistance receipt.
        earned = add(spm_unit, period, ["ca_sbd_general_relief_gross_earned_income"])
        # The first $10 and 20% of the balance are exempt per assistance
        # unit, applied after summing earned income to the unit. The floor
        # also keeps self-employment losses from offsetting unearned income.
        countable_earned = max_(earned - p.earned_exemption.flat, 0) * (
            1 - p.earned_exemption.rate
        )
        # Unearned income counts in full, with no exemptions or deductions.
        unearned = add(
            spm_unit, period, ["ca_sbd_general_relief_gross_unearned_income"]
        )
        # Like an excluded member's SSI, their SSP counts toward the unit's
        # pooled income; ca_state_supplement is an SPM-unit-level variable,
        # so it is added here rather than in the person-level unearned
        # sources list.
        ssp = spm_unit("ca_state_supplement", period)
        return countable_earned + unearned + ssp
