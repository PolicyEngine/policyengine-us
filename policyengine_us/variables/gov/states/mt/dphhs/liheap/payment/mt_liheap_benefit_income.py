from policyengine_us.model_api import *


class mt_liheap_benefit_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Montana LIHEAP annual income for the benefit calculation"
    defined_for = StateCode.MT
    reference = (
        # PDF pages 28-30, 127, 129-131
        "https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=28",
        # PDF pages 25-30, 125
        "https://web.archive.org/web/20260915040544/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=25",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap.categorical
        categorical = spm_unit("mt_liheap_categorical_eligibility", period)
        # Other households, including SNAP categorical ones, use countable
        # income; for SNAP households it carries no premium deduction and
        # stands in for the SNAP case's gross monthly income.
        countable_income = spm_unit("mt_liheap_countable_income", period)
        # SSI or TANF categorical households use only the current standard SSI
        # and TANF amounts, ignoring other income (manual section 3.11 and
        # Appendix A). The standards in effect at the start of the heating
        # season apply.
        ssi_date = period.start.offset(-int(p.ssi_year_lag), "year")
        p_ssi = parameters(ssi_date).gov.ssa.ssi.amount
        person = spm_unit.members
        receives_ssi = person("mt_liheap_receives_ssi", period)
        # A married couple who both receive SSI share the couple standard.
        marital_recipients = person.marital_unit.sum(receives_ssi)
        couple = receives_ssi & (marital_recipients > 1)
        monthly_ssi_standard = where(
            couple,
            p_ssi.couple / max_(marital_recipients, 1),
            p_ssi.individual,
        )
        ssi_standard = MONTHS_IN_YEAR * spm_unit.sum(
            where(receives_ssi, monthly_ssi_standard, 0)
        )
        # The TANF payment standard for the assistance unit, rounded to whole
        # dollars as Appendix A prints it.
        monthly_tanf_standard = (
            spm_unit("mt_tanf_payment_standard", period, options=[ADD]) / MONTHS_IN_YEAR
        )
        tanf_standard = where(
            spm_unit("tanf", period) > 0,
            MONTHS_IN_YEAR * np.floor(monthly_tanf_standard + 0.5),
            0,
        )
        return where(
            categorical == categorical.possible_values.SSI_TANF,
            ssi_standard + tanf_standard,
            countable_income,
        )
