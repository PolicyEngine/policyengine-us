from policyengine_us.model_api import *


class ky_federal_agi(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income allocated to each Kentucky filer"
    documentation = (
        "Federal AGI reported in Kentucky's separate-return columns, with allowed "
        "business and capital losses assigned to their owners. Other adjustments "
        "use the federal model's existing person allocations."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29032",
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions.pdf#page=13",
    )

    def formula(person, period, parameters):
        federal_agi = person("adjusted_gross_income_person", period)
        if "loss_ald" not in parameters(period).gov.irs.ald.deductions:
            return federal_agi

        # KRS 141.016(3): income and business deductions belong to the
        # spouse to whom they are attributable. Undo the loss allocation
        # actually included in federal person AGI before applying Kentucky's
        # allocation, so an already-owned loss is not reassigned twice.
        filing_status = person.tax_unit("filing_status", period)
        is_filer = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        share = is_filer * where(
            filing_status == filing_status.possible_values.JOINT, 0.5, 1.0
        )
        loss = person.tax_unit("loss_ald", period)
        capital_loss = min_(
            loss,
            add(
                person.tax_unit,
                period,
                ["capital_losses_allowed_against_gains", "limited_capital_loss"],
            ),
        )
        business_loss = max_(loss - capital_loss, 0)
        not_dependent = ~person("is_tax_unit_dependent", period)
        owned_business_loss = 0
        # Each Schedule C category's loss counts on its own, as in loss_ald.
        for source in (
            "self_employment_income",
            "sstb_self_employment_income",
            "farm_operations_income",
            "rental_income",
            "farm_rent_income",
            "estate_income",
            "partnership_s_corp_income",
        ):
            owned_business_loss += not_dependent * max_(-person(source, period), 0)
        # The existing tax-unit other_net_gain input has no owner. Preserve
        # its shared allocation rather than inventing one.
        owned_business_loss += share * max_(
            -person.tax_unit("other_net_gain", period), 0
        )
        owned_capital_loss = not_dependent * person("capital_losses", period)

        def allocate(owned, allowed):
            total = person.tax_unit.sum(owned)
            # Preserve existing sharing for explicit tax-unit deductions
            # without any person-level ownership inputs.
            proportion = where(total > 0, owned / where(total > 0, total, 1), share)
            return allowed * proportion

        # Keep business and capital pools separate so their different federal
        # limits do not change either pool's allocation or the joint total.
        owned_loss = allocate(owned_business_loss, business_loss) + allocate(
            owned_capital_loss, capital_loss
        )
        # Match above_the_line_deductions_person's reconciliation when supplied
        # person loss amounts differ from the return's loss deduction. Keep
        # dependent amounts off the parents' return.
        filer_loss = not_dependent * person("loss_ald_person", period)
        federal_loss = filer_loss + (
            loss - person.tax_unit.sum(filer_loss)
        ) * filer_share(person, period, filer_loss)
        return federal_agi + federal_loss - owned_loss
