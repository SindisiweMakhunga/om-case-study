"""Allow Terraform applies only for creates and GitCommitHash-only updates."""

import json
import sys


def has_unknown(value):
    """Check nested plan values for Terraform unknown/sensitive flags."""
    if value is True:
        return True
    if isinstance(value, dict):
        return any(has_unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(has_unknown(v) for v in value)
    return False


def validate(plan):
    """Return a list of reasons the plan must be blocked (empty means allowed)."""
    errors = []
    # Refuse invalid, incomplete, or non-applyable plans.
    if plan.get('errored') or not plan.get('complete', False) or not plan.get('applyable', False):
        errors.append('Plan is not complete and applyable; regenerate the plan.')

    # Check each resource change in the Terraform plan.
    for resource in plan.get('resource_changes', []):
        change = resource['change']
        actions = change['actions']
        name = resource['address']

        # New resources and unchanged resources are safe.
        if actions in (['create'], ['no-op']):
            continue
        # Reject deletes, replacements, and all other action combinations.
        if actions != ['update']:
            errors.append(f'{name}: {actions} is not allowed; remove this action from the plan.')
            continue

        # For updates, compare the resource state before and after.
        before = change.get('before')
        after = change.get('after')
        if not isinstance(before, dict) or not isinstance(after, dict):
            errors.append(f'{name}: cannot compare update values; block apply.')
            continue

        # Only the top-level tags attribute may change.
        changed = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
        if changed - {'tags'}:
            errors.append(f'{name}: non-tag attributes changed: {sorted(changed - {"tags"})}; revert them.')

        # Within tags, only GitCommitHash may be added, changed, or removed.
        old_tags = before.get('tags') or {}
        new_tags = after.get('tags') or {}
        if not isinstance(old_tags, dict) or not isinstance(new_tags, dict):
            errors.append(f'{name}: tags cannot be compared; block apply.')
        else:
            changed_tags = {k for k in old_tags.keys() | new_tags.keys()
                            if old_tags.get(k) != new_tags.get(k)}
            if changed_tags - {'GitCommitHash'}:
                errors.append(f'{name}: forbidden tag changes: {sorted(changed_tags - {"GitCommitHash"})}; revert them.')

        # Block updates with unknown or sensitive values we cannot compare.
        if has_unknown(change.get('after_unknown', {})) or has_unknown(change.get('after_sensitive', {})):
            errors.append(f'{name}: update has unknown or sensitive values; cannot verify it safely.')

    return errors


if __name__ == '__main__':
    # Run with: python script.py tfplan.json
    if len(sys.argv) != 2:
        sys.exit('Usage: python script.py <tfplan.json>')
    try:
        with open(sys.argv[1], encoding='utf-8') as f:
            plan = json.load(f)
        errors = validate(plan)  # Validate the loaded plan.
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.exit(f'BLOCK APPLY: Invalid plan: {exc}')

    # A nonzero exit code blocks CI/CD pipelines from applying the plan.
    if errors:
        print('BLOCK APPLY: Do not run terraform apply.')
        for error in errors:
            print('-', error)
        sys.exit(1)

    print('PROCEED WITH APPLY: All changes comply with the policy.')


