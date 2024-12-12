import json
import subprocess
from datetime import datetime, UTC
import argparse
import sys

def run_command(command) -> str:
    """
    Run a shell command and return the output
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e.stderr}", file=sys.stderr)
        raise

def get_resources_with_expiry(namespace=None):
    """
    Find all resources w/ the required annotation (cloudbees/expiry)
    """
    cmd = ["kubectl", "get", "all", "-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])
    else:
        cmd.extend(["-A"])

    output = run_command(cmd)
    resources = json.loads(output)

    expired_releases = set()
    now = datetime.now(UTC)

    for item in resources["items"]:
        annotations = item.get("metadata", {}).get("annotations", {})
        expiry = annotations.get("cloudbees/expiry")

        helm_release = annotations.get("meta.helm.sh/release-name")
        helm_release_namespace = annotations.get("meta.helm.sh/release-namespace")

        if expiry and helm_release:
            try:
                expiry_date = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                if now > expiry_date:
                    expired_releases.add((helm_release, helm_release_namespace))
            except ValueError as e:
                print(f"Warning: Invalid date format for resource {item.get('metadata', {}).get('name')}: {e}", file=sys.stderr)

    return expired_releases

def cleanup_releases(releases, dry_run=True):
    """
    Uninstall the given Helm releases
    """
    for release in releases:
        release_name = release[0]
        release_namespace = release[1]
        cmd = ["helm", "uninstall", release_name, "-n", release_namespace]
        if dry_run:
            print(f"[DRY RUN] Would uninstall release: {release}")
            continue

        try:
            output = run_command(cmd)
            print(f"Succesfully uninstalled release: {release}")
            print(output)

        except subprocess.CalledProcessError:
            print(f"Failed to uninstall release: {release}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Cleanup expired Helm releases")
    parser.add_argument('--namespace', '-n', help="Kubernetes namespace to check")
    parser.add_argument('--dry-run', action='store_true', help='Print actions without executions them')
    args = parser.parse_args()

    try:
        print("Finding expired releases...")
        expired_releases = get_resources_with_expiry(args.namespace)

        if not expired_releases:
            print("No expired releases found.")
            return

        print(f"\nFound {len(expired_releases)} expired release(s):")
        for release in expired_releases:
            print(f"- {release[0]} ({release[1]})")

        print("\nProceeding with cleanup...")
        cleanup_releases(expired_releases, args.dry_run)


    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
