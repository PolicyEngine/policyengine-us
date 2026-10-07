from policyengine_us.model_api import *


class dc_separate_capital_loss_adjustment(Variable):
    value_type = float
    entity = Person
    label = "DC capital loss adjustment when spouses file separately on the same return"
    unit = USD
    documentation = (
        "For the head and spouse of a joint federal return, the amount added "
        "to their DC AGI when they file separately on the same DC return. "
        "Each spouse's federal AGI includes their share of the couple's "
        "capital loss deduction, in proportion to their own capital losses. "
        "Filing separately, each spouse instead deducts their own capital "
        "losses up to their own capital gains plus $1,500, the limit for "
        "married people filing separately. The adjustment is the first amount "
        "less the second. It does not apply to the joint DC computation, "
        "which keeps the federal joint deduction."
    )
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = (
        # Line c: "The maximum allowable annual capital loss claim is $3000
        # ($1500 if married or registered domestic partner filing
        # separately)."
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2024_D40_Booklet_062325.pdf#page=16",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D40_Book_082026_v1.pdf#page=19",
        # Schedule S, Calculation J: each spouse's portion of federal AGI.
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D40_Book_082026_v1.pdf#page=51",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.irs
        capital_losses = person("capital_losses", period)
        # The spouse's part of the federal capital loss deduction, as in
        # loss_ald_person: losses against gains plus the net loss up to
        # $3,000, in proportion to each spouse's own capital losses.
        capital_share = filer_share(person, period, capital_losses)
        federal = (
            person("limited_capital_loss_person", period)
            + tax_unit("capital_losses_allowed_against_gains", period) * capital_share
        )
        # As in capital_losses_allowed_against_gains: no capital loss
        # deduction when a reform takes capital gains out of gross income.
        sources = p.gross_income.sources
        if "capital_gains" not in sources:
            return 0 * federal
        # Filing separately, the spouse's own capital gains, including capital
        # gain distributions, absorb their own losses first, and the net loss
        # deductible is at most $1,500.
        gains = 0
        for source in ["capital_gains", "non_sch_d_capital_gains"]:
            if source in sources:
                gains = gains + max_(0, person(source, period))
        separate_limit = p.ald.loss.capital.max["SEPARATE"]
        separate = min_(capital_losses, gains + separate_limit)
        return joint * head_or_spouse * (federal - separate)
