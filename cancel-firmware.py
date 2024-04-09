import asyncio
import meraki.aio
import os
import time

RETRIES = 5  # max number of retries per call for 429 rate limit status code

org_id = os.environ.get('MERAKI_ORG_ID')


async def get_org_networks(aiomeraki: meraki.aio.AsyncDashboardAPI, orgid):
    print(f'getting networks for org ID {orgid}')
    try:
        networks = await aiomeraki.organizations.getOrganizationNetworks(organizationId=orgid)
        return networks
    except meraki.AsyncAPIError as e:
        print(f"Meraki API error: {e}")
        return False
    except Exception as e:
        print(f"some other error: {e}")
        return False

# Function to get firmware upgrade status
async def get_firmware_upgrades(aiomeraki: meraki.aio.AsyncDashboardAPI, network_id):
    try:
        firmwareUpgrades = await aiomeraki.networks.getNetworkFirmwareUpgrades(network_id)
        return firmwareUpgrades
    except meraki.AsyncAPIError as e:
        print(f'Meraki API error: {e}')
        return
    except Exception as e:
        print(f'The following error has occurred: {e}')
        return

# Function to cancel any firmware upgrades for a network
async def cancel_firmware_upgrades(aiomeraki: meraki.aio.AsyncDashboardAPI, network_id):
    # Build dict for updating firmware upgrades on network
    resetJson = {}
    # keep audit of current state for any products that will be canceled
    fwchanges = {}
    # Grab current firmware upgrade states
    fwstate = await get_firmware_upgrades(aiomeraki, network_id)
    # look for any product types with an upgrade scheduled
    for productType, value in fwstate['products'].items():
        if(len(value['nextUpgrade']['time']) > 0):
            resetJson[productType] = {'nextUpgrade': {'toVersion':value['currentVersion']}}
            fwchanges[productType] = {'currentVersion': value['currentVersion'],
                                      'nextUpgrade': value['nextUpgrade']}
    # if there are products that need firmware canceled...
    if len(resetJson) > 0:
        try:
            await aiomeraki.networks.updateNetworkFirmwareUpgrades(network_id, products = resetJson)
            return (network_id, fwchanges)
        except meraki.AsyncAPIError as e:
            print(f'Meraki API error: {e}')
            return
        except Exception as e:
            print(f'The following error has occurred: {e}')
            return


# Main function to run the script
async def main():
    # Prompt the user for the API key, organization ID, and tag to filter on
    print(f"This script will cancel any existing firmware upgrades for org ID {org_id}!")
    print("")
    tag = input("[Optional] Specify an existing network tag to skip canceling firmware upgrades on any network with said tag (e.g., 'KEEP_FW_UPGRADE'): ")

    startTime = time.time_ns()

    async with meraki.aio.AsyncDashboardAPI(
        log_file_prefix=__file__[:-3],
        print_console=False,
        maximum_retries=RETRIES
    ) as aiomeraki:
        # define vars
        get_tasks = []
        cancelfw_results = []
        netlist = {}

        # Get all networks that are tagged with specified tag
        networks = await get_org_networks(aiomeraki, org_id)
        for net in networks:
            netlist[net['id']] = net['name']
            if len(tag) > 0:
                if tag not in net['tags']:
                    # cancel any upgrades
                    get_tasks.append(cancel_firmware_upgrades(aiomeraki, net['id']))
            else:
                get_tasks.append(cancel_firmware_upgrades(aiomeraki, net['id']))

        print("Looking for networks with pending firmware upgrades...")
        # Run through networks looking for firmware upgrades to cancel
        for task in asyncio.as_completed(get_tasks):
            cancelfw = await task
            cancelfw_results.append(cancelfw)

        for result in cancelfw_results:
            if(result):
                for productType, value in result[1].items():
                    print(f'Firmware upgrades for network "{netlist[result[0]]}" - product "{productType}" canceled! Canceling upgrade to {value['nextUpgrade']['toVersion']['shortName']}; staying on {value['currentVersion']['shortName']} instead.')
    endTime = time.time_ns()
    print(f'Total time to run: {(endTime - startTime)/1000000} ms')

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())