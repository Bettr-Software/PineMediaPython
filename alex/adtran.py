# import textfsm
# from netmiko import ConnectHandler
# from itertools import chain
#
# #!/usr/bin/env python3
# import argparse
#
# def setup_args():
#     parser = argparse.ArgumentParser(description='Generate the required config for an Adtran OLT to deploy an ONT')
#     parser.add_argument('serial', help='Serial number of the ONT')
#     parser.add_argument('ont_desc', help='Description for ONT in "quotes"')
#     parser.add_argument('-d', '--dhcp', action='store_true', help='Generate config for a client using DHCP')
#     parser.add_argument('-v', '--dhcpv6', action='store_true', help='Generate config for a client using DHCPv6')
#     parser.add_argument('-p', '--pppoe', action='store_true', help='Generate config for a client using PPPoE')
#     parser.add_argument('-P', '--pop', action='store_true', help='Generate config for a POP as opposed to a residential ONT')
#     parser.add_argument('-S', '--svlan', type=int, help='Specify SVLAN to use. Only needed for POP configs')
#     return parser.parse_args()
#
# ###########################################################################################################
#
# #Define device connection details
# testolt = { 'device_type': 'adtran_os',
#         'ip': '10.0.10.10',
#         'username': 'ADMIN',
#         'password': 'PineMedia01!',
#         'session_log': 'adtran_output.txt'
#         }
#
# ####################################################################################################################
#
# def find_ssp_for_ont(): #Function to find the shelf/slot/port information for the inactive ONT
#     global oltshelf
#     global oltslot
#     global oltport
#     cfg = f'show table remote-devices inactive | include {args.serial}'
#     all_devices = [testolt]
#     with open('adtran_sspinactive_output.txt', 'w') as o: #Output processes to a text file for debugging
#         for devices in all_devices: #Repeat the below for each device
#             net_connect = ConnectHandler(**devices) #Tells netmiko to connect to all devices in the devices list
#             net_connect.enable() #Enter enable mode
#             net_connect.send_command('terminal width 132') #Set large terminal width else netmiko gets verrry confused
#             output = net_connect.send_command(cfg) #Send command
#             o.write(output)
#
#     with open('inactiveontsparse.template') as template: #Open textfsm template
#         fsm = textfsm.TextFSM(template) #Process the output with textfsm
#         parsedresult = fsm.ParseText(output) #Parse the output into a usable variable
#         reducedlist = list(chain.from_iterable(parsedresult)) #Converts original output of list within list into a single list
#
#         oltshelf = reducedlist[0]
#         oltslot = reducedlist[1]
#         oltport = reducedlist[2]
#
#
# ###########################################################################################################
#
# def find_lowest_available_ont(): #Function to find the lowest available ONT
#     global lowestontid
#     cfg = f'show table remote-devices ont @{oltshelf}/{oltslot}/{oltport}'
#     all_devices = [testolt]
#     with open('adtran_lowestont_output.txt', 'w') as o: #Output processes to a text file for debugging
#         for devices in all_devices: #Repeat the below for each device
#             net_connect = ConnectHandler(**devices) #Tells netmiko to connect to all devices in the devices list
#             net_connect.enable() #Enter enable mode
#             net_connect.send_command('terminal width 132') #Set large terminal width else netmiko gets verrry confused
#             output = net_connect.send_command(cfg) #Send command
#             o.write(output)
#
#     with open('ontidparse.template') as template: #Open textfsm template
#         fsm = textfsm.TextFSM(template) #Process the output with textfsm
#         parsedresult = fsm.ParseText(output) #Parse the output into a usable variable
#
#     reducedlist = list(chain.from_iterable(parsedresult)) #Converts original output of list within list into a single list
#     reducedintlist = [int(x) for x in reducedlist] #Converts string list into integer list
#     def find_missing(reducedintlist):
#         return sorted(set(range(1, 129)) - set(reducedintlist)) #Finds missing numbers within the list between 1 and (not including) 129
#
#     missingvalues = (find_missing(reducedintlist)) #Sets variable for missing numbers within the list
#     smallestmissinglist = (missingvalues[:1]) #Finds the smallest missing number
#     lowestontid = (','.join(map(str, smallestmissinglist))) #Removes the number from the list
#
# ################################################################################################################################
#
# def generate_config(): #Function to generate the configuration
#
#     global config
#     config = f'\n'
#     if args.pop == True:
#         # Create new EVC for the POP
#         config += f'evc "POP_{args.ont_desc}"\n'
#         config += f's-tag {args.svlan}\n'
#         config += f'connect men-port default-ethernet\n'
#         config += f'no mac-switched\n'
#         config += f'no preserve-ce-vlan\n'
#         config += f'no shutdown\n'
#         config += f'\n'
#         # Create the POP's management evc-map
#         config += f'evc-map "pop_management_{lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}" {oltshelf}/{oltslot}\n'
#         config += f'connect evc "POP_{args.ont_desc}"\n'
#         config += f'connect uni gigabit-ethernet {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}.gpon\n'
#         config += f'connect gpon upstream channel 1\n'
#         config += f'match ce-vlan-id 111\n'
#         config += f'men-pri 0\n'
#         config += f'men-c-tag-pri 0\n'
#         config += f'subscriber access dhcp mode transparent\n'
#         config += f'subscriber access dhcpv6 mode transparent\n'
#         config += f'subscriber access pppoe mode transparent\n'
#         config += f'subscriber arp mode transparent\n'
#         config += f'subscriber igmp mode transparent\n'
#         config += f'no shutdown\n'
#         config += f'exit\n'
#         config += f'\n'
#         # Create the evc-map for dhcp clients
#         config += f'evc-map "customer_data_popdhcp_{lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}" {oltshelf}/{oltslot}\n'
#         config += f'connect evc "Cust_DHCP"\n'
#         config += f'connect uni gigabit-ethernet {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}.gpon\n'
#         config += f'connect gpon upstream channel 1\n'
#         config += f'match ce-vlan-id 4062\n'
#         config += f'men-pri 0\n'
#         config += f'men-c-tag-pri 0\n'
#         config += f'subscriber access dhcp mode authenticate\n'
#         config += f'subscriber access dhcpv6 mode block\n'
#         config += f'subscriber access pppoe mode block\n'
#         config += f'subscriber access dhcp option-82 circuit-id "$ont$/$ontslot$/$ontport$@$shelf$/$slot$/$port$"\n'
#         config += f'subscriber access dhcp option-82\n'
#         config += f'subscriber arp mode proxy\n'
#         config += f'no shutdown\n'
#         config += f'exit\n'
#         config += f'\n'
#         # Create the evc-map for pppoe clients
#         config += f'evc-map "customer_data_poppppoe_{lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}" {oltshelf}/{oltslot}\n'
#         config += f'connect evc "Cust_PPPoE"\n'
#         config += f'connect uni gigabit-ethernet {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}.gpon\n'
#         config += f'connect gpon upstream channel 1\n'
#         config += f'match ce-vlan-id 4063\n'
#         config += f'men-pri 0\n'
#         config += f'men-c-tag-pri 0\n'
#         config += f'subscriber access dhcp mode block\n'
#         config += f'subscriber access dhcpv6 mode block\n'
#         config += f'subscriber access pppoe mode authenticate\n'
#         config += f'subscriber arp mode proxy\n'
#         config += f'no shutdown\n'
#         config += f'exit\n'
#     else:
#         # Config for ONTs that aren't POPs
#         config += f'evc-map "customer_data_{lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}" {oltshelf}/{oltslot}\n'
#         if args.dhcp == True or args.dhcpv6 == True:
#             config += f'connect evc "Cust_DHCP"\n'
#         if args.pppoe == True:
#             config += f'connect evc "Cust_PPPoE"\n'
#         config += f'connect uni gigabit-ethernet {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}.gpon\n'
#         config += f'connect gpon upstream channel 1\n'
#         config += f'match untagged\n'
#         config += f'men-pri 0\n'
#         config += f'men-c-tag-pri 0\n'
#         if args.dhcp == True:
#             config += f'subscriber access dhcp mode authenticate\n'
#             config += f'subscriber access dhcp option-82 circuit-id {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}\n'
#             config += f'subscriber access dhcp option-82\n'
#         if args.dhcp == False:
#             config += f'subscriber access dhcp mode block\n'
#         if args.dhcpv6==True:
#             config += f'subscriber access dhcpv6 mode authenticate\n'
#         if args.dhcpv6==False:
#             config += f'subscriber access dhcpv6 mode block\n'
#         if args.pppoe==True:
#             config += f'subscriber access pppoe mode authenticate\n'
#         if args.pppoe==False:
#             config += f'subscriber access pppoe mode block\n'
#         config += f'subscriber arp mode proxy\n'
#         config += f'no shutdown\n'
#         config += f'exit\n'
#     config += f'\n'
#     config += f'shaper "{lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}_US" {lowestontid}@{oltshelf}/{oltslot}/{oltport}.gpon\n'
#     config += f'per interface gpon {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}.gpon channel 1\n'
#     config += f'rate 1000000\n'
#     config += f'gpon channel assured-bandwidth 0\n'
#     config += f'gpon channel fixed-bandwidth 0\n'
#     config += f'min-rate 0\n'
#     config += f'no shutdown\n'
#     config += f'exit\n'
#     config += f'\n'
#     config += f'shaper "{lowestontid}@{oltshelf}/{oltslot}/{oltport}_DS" {oltshelf}/{oltslot}\n'
#     config += f'per remote-device {lowestontid}@{oltshelf}/{oltslot}/{oltport}.gpon queue 0\n'
#     config += f'rate 1000000\n'
#     config += f'min-rate 0\n'
#     config += f'no shutdown\n'
#     config += f'exit\n'
#     config += f'\n'
#     config += f'remote-device ont {lowestontid}@{oltshelf}/{oltslot}/{oltport}\n'
#     config += f'serial-number {args.serial}\n'
#     if args.pop == True:
#         args.ont_desc = "POP_" + args.ont_desc
#     config += f'description "{args.ont_desc}"\n'
#     config += f'no mac-spoofing-allowed enable\n'
#     config += f'aes\n'
#     config += f'no shutdown\n'
#     config += f'exit\n'
#     config += f'\n'
#     config += f'interface gigabit-ethernet {lowestontid}/0/1@{oltshelf}/{oltslot}/{oltport}.gpon\n'
#     if args.pop == True:
#         config += f'mac limit disabled\n'
#     else:
#         config += f'mac limit 2\n'
#     config += f'no shut\n'
#     config += f'exit\n'
#     config += f'exit\n'
#     return config
#
# #################################################################################################################
#
# def apply_config(): #Function to apply the config to the OLT
#     #Apply the config to the OLT here
#     cfg = f'show table remote-devices ont @{oltshelf}/{oltslot}/{oltport}'
#     all_devices = [testolt]
#     with open('adtran_configapply.txt', 'w') as o: #Output processes to a text file for debugging
#         for devices in all_devices: #Repeat the below for each device
#             net_connect = ConnectHandler(**devices) #Tells netmiko to connect to all devices in the devices list
#             net_connect.enable() #Enter enable mode
#             net_connect.send_command('terminal width 132') #Set large terminal width else netmiko gets verrry confused
#             output = net_connect.send_config_set(config, cmd_verify=False) #Send command
#             o.write(output) #Write output to file
#
# ####################################################################################################################

def run_from_app(serial, desc):
    return serial + "in alex's script" + desc + "in alex's script"

# if __name__ == '__main__':
#     # process arguments
#     args = setup_args()
#     if args.pop == False:
#         # stop the script and warn the user if pppoe and dhcp or dhcpv6 have been selected
#         if (args.dhcp==True and args.pppoe==True) or (args.dhcpv6==True and args.pppoe==True):
#             print('\033[2;31;43mWARNING: PPPoE can only be used on its own and cannot be used with DHCP or DHCPv6.')
#             print('Exiting...\033[0;0m')
#             exit()
#             # stop the script and warn the user if no authentication method has been selected
#         if (args.dhcp==False and args.dhcpv6==False and args.pppoe==False):
#             print('\033[2;31;43mWARNING: An authentication method must be selected.')
#             print('Exiting...\033[0;0m')
#             exit()
#     else:
#         # stop the script and warn the user if pppoe, dhcp or dhcpv6 have been selected with the POP configure
#         if args.dhcp==True or args.pppoe==True or args.dhcpv6==True:
#             print('\033[2;31;43mWARNING: POP configs cannot have authentication methods selected')
#             print('Exiting...\033[0;0m')
#             exit()
#         # stop the script and warn the user if no SVLAN has been specified when making a POP config
#         if args.svlan==None and args.pop==True:
#             print('\033[2;31;43mWARNING: POP configs must specify an SVLAN')
#             print('Exiting...\033[0;0m')
#             exit()
#     print('\n=== 1. Finding inactive ONT information ===\n')
#     find_ssp_for_ont()
#     print('\n=== 2. Finding lowest available ONT ID ===\n')
#     find_lowest_available_ont()
#     print('\n=== 3. Generating config for OLT ===\n')
#     generate_config()
#     print('\n=== 4. Applying generated config to OLT ===\n')
#     apply_config()
#     print('\n=== 5. Config applied successfully ===\n')
