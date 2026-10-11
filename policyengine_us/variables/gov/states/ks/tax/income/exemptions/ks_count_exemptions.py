from policyengine_us.model_api import *


class ks_count_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "number of KS exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip22.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip23.pdf#page=6",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        joint = filing_status == statuses.JOINT
        hoh = filing_status == statuses.HEAD_OF_HOUSEHOLD
        adults = where(joint | hoh, 2, 1)
        # Dependents are those "you claim as a dependent" federally; under IRC
        # 152(b)(1) a return on which the filer (or, if joint, either spouse)
        # can be claimed has none, unless the would-be claimant meets the
        # filing exception (Publication 501, Dependent Taxpayer Test).
        no_dependents = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        dependents = where(no_dependents, 0, tax_unit("tax_unit_dependents", period))
        # K-40 instructions: "If you are claimed as a dependent by another
        # taxpayer, enter '0' in the Total Kansas exemptions box." Applied when
        # either spouse on a joint return is claimed.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        filer_claimed = tax_unit.any(filer & claimed)
        return where(filer_claimed, 0, adults + dependents)
