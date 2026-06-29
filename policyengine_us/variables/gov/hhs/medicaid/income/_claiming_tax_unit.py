from policyengine_us.model_api import *


NO_MEDICAID_CLAIMING_TAX_UNIT_ID = 0


def _sum_by_positive_id(target_id, member_id, values):
    target_id = np.asarray(target_id).astype(int)
    member_id = np.asarray(member_id).astype(int)
    values = np.asarray(values, dtype=float)
    result = np.zeros_like(target_id, dtype=float)
    valid_members = member_id > NO_MEDICAID_CLAIMING_TAX_UNIT_ID

    if not np.any(valid_members):
        return result

    unique_ids, inverse = np.unique(member_id[valid_members], return_inverse=True)
    sums = np.bincount(
        inverse,
        weights=values[valid_members],
        minlength=len(unique_ids),
    )
    index = np.searchsorted(unique_ids, target_id)
    safe_index = np.clip(index, 0, len(unique_ids) - 1)
    matched = (target_id > NO_MEDICAID_CLAIMING_TAX_UNIT_ID) & (
        unique_ids[safe_index] == target_id
    )
    return where(matched, sums[safe_index], result)


def _value_by_positive_id(target_id, member_id, values, selector):
    target_id = np.asarray(target_id).astype(int)
    member_id = np.asarray(member_id).astype(int)
    values = np.asarray(values, dtype=float)
    selector = np.asarray(selector).astype(bool)
    result = np.zeros_like(target_id, dtype=float)
    valid_members = (member_id > NO_MEDICAID_CLAIMING_TAX_UNIT_ID) & selector

    if not np.any(valid_members):
        return result

    valid_member_id = member_id[valid_members]
    valid_values = values[valid_members]
    unique_ids, index = np.unique(valid_member_id, return_index=True)
    selected_values = valid_values[index]
    lookup_index = np.searchsorted(unique_ids, target_id)
    safe_index = np.clip(lookup_index, 0, len(unique_ids) - 1)
    matched = (target_id > NO_MEDICAID_CLAIMING_TAX_UNIT_ID) & (
        unique_ids[safe_index] == target_id
    )
    return where(matched, selected_values[safe_index], result)


def medicaid_external_claimed_sum(person, period, target_tax_unit_id, values):
    current_tax_unit_id = person.tax_unit("tax_unit_id", period)
    claiming_tax_unit_id = person("medicaid_claiming_tax_unit_id", period)
    external_claim = person("medicaid_has_known_claiming_tax_unit", period) & (
        claiming_tax_unit_id != current_tax_unit_id
    )

    return _sum_by_positive_id(
        target_tax_unit_id,
        claiming_tax_unit_id,
        values * external_claim,
    )


def medicaid_claiming_tax_unit_value(person, period, values):
    claiming_tax_unit_id = person("medicaid_claiming_tax_unit_id", period)
    current_tax_unit_id = person.tax_unit("tax_unit_id", period)
    tax_unit_head = person("is_tax_unit_head", period)
    return _value_by_positive_id(
        claiming_tax_unit_id,
        current_tax_unit_id,
        values,
        tax_unit_head,
    )
