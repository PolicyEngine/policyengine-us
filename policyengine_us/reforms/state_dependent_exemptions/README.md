The following adjustments have been made in this reform:
Alabama: Neutralize dependent exemptions
California: Remove the dependent exemption structure from `ca_exemptions`
Georgia: Remove the dependent exemption structure from `ga_exemptions`
Hawaii: Change the `exemptions_count` to `head_spouse_count_not_dependent_elsewhere`
Illinois: Neutralize dependent exemptions
Indiana: Change the `tax_unit_size` to `head_spouse_count`
Iowa: Remove the dependent exemption structure from `ia_exemption_credit`
Kansas: Remove the dependents from the exemption count
Louisiana: Neutralize dependent exemptions
Maryland: Change the `tax_unit_size` to `head_spouse_count`
Massachusetts: Remove the dependent exemption structure from `ma_income_tax_exemption_threshold`
Michigan: Change the `tax_unit_size` to `head_spouse_count`
Minnesota: Neutralize dependent exemptions
Mississippi: Neutralize dependent exemptions
Montana: Neutralize the dependent exemptions person
Nebraska: Change the `tax_unit_size` to `head_spouse_count`
New Jersey: Neutralize dependent exemptions
New Mexico: Neutralize the deduction for certain dependents
New York: Neutralize dependent exemptions
North Carolina: Neutralize the child deduction
Ohio: Remove `is_tax_unit_dependent` from the exemption eligibility criteria
Oklahoma: Remove the dependents from the total exemptions
Rhode Island: Change the `exemptions_count` to `head_spouse_count_not_dependent_elsewhere`
South Carolina: Neutralize dependent exemptions
Utah: Neutralize the personal exemption amount
Vermont: Remove the dependents from the personal exemptions, counting `head_spouse_count_not_dependent_elsewhere`
Virginia: Only apply the personal exemptions to a head or spouse who cannot be claimed as a dependent
West Virginia: Change the `exemptions_count` to `head_spouse_count_not_dependent_elsewhere`
Wisconsin: Change the `exemptions_count` to `head_spouse_count_not_dependent_elsewhere`
Arizona: Neutralize dependent exemptions
Arkansas: Neutralize dependent exemptions
Delaware: Change the `exemptions_count` to `head_spouse_count_not_dependent_elsewhere`
Idaho: Neutralize dependent exemptions CTC
Iowa: Change the `tax_unit_size` to `head_spouse_count`
Kentucky: Change the `tax_unit_size` in family_size to `head_spouse_count`
Maine: Neutralize dependent exemptions
Nebraska: Change the `tax_unit_size` to `head_spouse_count`
Oklahoma: Remove CTC portion and update return

Where a state's baseline gives no personal exemption (in Oklahoma, no regular exemption) to a filer who can be claimed as a dependent on another return (Delaware, Hawaii, Michigan, Ohio, Oklahoma, Rhode Island, Vermont, Virginia, West Virginia and Wisconsin), the reform keeps that rule. Michigan's baseline `mi_exemptions` bypasses `mi_personal_exemptions` for such a return, and Ohio's override already reads `claimed_as_dependent_on_another_return`. The other states' baselines count every head and spouse, so their overrides do too.
