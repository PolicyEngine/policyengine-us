from policyengine_us.model_api import *


class mt_liheap_receives_ssi(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Receives SSI for Montana LIHEAP"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/5475239b875d29ebe7cf1f12b38458830f87a4a18c8dd600b7548603204fccd9#page=1",
        # PDF pages 28-30
        "https://web.archive.org/web/20261015032646/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=28",
    )

    def formula(person, period, parameters):
        # A computed payment or reported receipt in any month qualifies.
        # receives_ssi is a monthly flag: read each month explicitly rather
        # than requesting an annual aggregate, which would cache a summed
        # value under the annual key and change what other formulas read.
        first_month = period.first_month
        reported_any_month = np.any(
            [
                person("receives_ssi", first_month.offset(month_offset))
                for month_offset in range(MONTHS_IN_YEAR)
            ],
            axis=0,
        )
        return (add(person, period, ["ssi"]) > 0) | reported_any_month
