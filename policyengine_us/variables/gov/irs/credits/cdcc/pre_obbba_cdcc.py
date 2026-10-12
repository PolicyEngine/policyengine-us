from policyengine_us.model_api import *


class pre_obbba_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal CDCC before the section 26 cap, pre-OBBBA section 21 rate"
    documentation = (
        "The federal child and dependent care credit before the section 26 "
        "liability cap, recomputed with the IRC section 21 rate schedule as it "
        "stood before the One Big Beautiful Bill Act (OBBBA). States whose "
        "income tax statically conforms to a pre-2026 IRC read this instead of "
        "the live federal credit so they do not silently adopt the OBBBA "
        "section 21 rate increase, effective for tax years beginning after "
        "2025-12-31."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#a_2"

    def formula(tax_unit, period, parameters):
        # Only the section 21(a)(2) rate schedule changed under OBBBA
        # (phase_out.max 0.35->0.50, phase_out.min 0.20->0.35, plus a new
        # amended second phase-out), all dated 2026-01-01. The section 21(b)-(e)
        # expense base is unchanged, so freeze only the rate by reading the cdcc
        # parameter subtree at a pre-OBBBA instant. Any 2023-2025 instant yields
        # the same schedule; use 2025-01-01. The pre-OBBBA schedule has no
        # second phase-out after 2021 (second_start is infinite from 2022), so
        # the first phase-out is the whole rate computation.
        frozen = parameters("2025-01-01").gov.irs.credits.cdcc
        agi = tax_unit("adjusted_gross_income", period)
        excess_agi = max_(0, agi - frozen.phase_out.start)
        increments = np.ceil(excess_agi / frozen.phase_out.increment)
        percentage_reduction = increments * frozen.phase_out.rate
        rate = max_(
            frozen.phase_out.min,
            frozen.phase_out.max - percentage_reduction,
        )
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        expenses = tax_unit("cdcc_relevant_expenses", period)
        return eligible * expenses * rate


class pre_obbba_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal CDCC (section 26 non-refundable cap), pre-OBBBA section 21 rate"
    documentation = (
        "Mirror of the live cdcc variable but built on the pre-OBBBA section 21 "
        "rate schedule, for states whose income tax statically conforms to a "
        "pre-2026 IRC."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        # cdcc has been non-refundable since 2022; every state that reads this
        # computes post-2022, so apply the section 26 liability cap directly
        # (the refundable-2021 branch of the live cdcc is not reachable here).
        potential = tax_unit("pre_obbba_cdcc_potential", period)
        credit_limit = tax_unit("cdcc_credit_limit", period)
        return min_(credit_limit, potential)


class pre_obbba_capped_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped federal CDCC (Credit Limit Worksheet), pre-OBBBA section 21 rate"
    documentation = (
        "Mirror of the live capped_cdcc variable but built on the pre-OBBBA "
        "section 21 rate schedule, for states whose income tax statically "
        "conforms to a pre-2026 IRC."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/instructions/i2441"

    def formula(tax_unit, period, parameters):
        cdcc = tax_unit("pre_obbba_cdcc", period)
        # 2022 Form 2441 Credit Limit Worksheet: cap at tax before credits less
        # the foreign tax credit (the section 26 cap is unchanged by OBBBA).
        itaxbc = tax_unit("income_tax_before_credits", period)
        offset = tax_unit("foreign_tax_credit", period)
        cap = max_(itaxbc - offset, 0)
        return min_(cdcc, cap)
