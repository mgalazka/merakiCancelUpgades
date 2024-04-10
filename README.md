# merakiCancelUpgades

**Warning:** This script allows for BAD BEHAVIOR by canceling all firmware upgrades that are scheduled. Know that firmware upgrades are important to Meraki, so this should be used sparingly and with caution.

## Meraki Cancel Firmware Upgrades
One key feature of the Meraki Dashboard is its automatic firmware upgrades. This allows Meraki hardware to stay up to date and reduce the risk of security vulnerabilities, increases stability, and generally provides more features over time. There are specific times when automatically-scheduled firmware upgrades can be a challenge. For instance, maybe when a change is in the midst of being planned for a particular maintenance window (and not approved yet), but automatic upgrades are scheduling changes prematurely. In cases like this, there may be a need to cancel firmware upgrades in an org to then work more selectively.

## Scripts

**cancel-firmware.py** - This is a script that leverages the Meraki Dashboard API with asyncio. It scans a specific Meraki organization for any scheduled firmware upgrades, and subsequently cancels them. It provides the option of specifying a 'safe' tag. Any network tagged with the tag provided to the script, will be skipped by this script. If there are specific networks that have legitimate upgrades scheduled, make sure you tag them, and then provide that tag to the script. Error handling in this script is limited, and performance for large orgs is unknown at this time.

## Usage Requirements
These scripts require that the following environment variables are set:

**MERAKI_DASHBOARD_API_KEY** - this should be set to the API key copied from Dashboard.

**MERAKI_ORG_ID** - this should be set to the Meraki Org ID that represents the Meraki organization to be targeted by this script. Org ID can be pulled either via API (https://developer.cisco.com/meraki/api/get-organizations/) or by looking at the footer of any page on the Meraki Dashboard when logged in.

## Example usage
./cancel-firmware.py

```
This script will cancel any existing firmware upgrades for org ID 12345!

[Optional] Specify an existing network tag to skip canceling firmware upgrades on any network with said tag (e.g., 'KEEP_FW_UPGRADE'): KEEP_FW_UPGRADE
getting networks for org ID 12345
Looking for networks with pending firmware upgrades...
Firmware upgrades for network "Teleworker-Z4C" - product "appliance" canceled! Canceling upgrade to MX 18.210; staying on MX 18.207 instead.
Total time to run: 2935.361 ms
```

## General disclaimer
This is proof of concept code and should be treated as such. There is very limited error handling in this project, and testing has been light. Please test this in small orgs and scopes.
