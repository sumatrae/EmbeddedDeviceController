import yaml
import socket
import time
import os
import ipaddress

def send_msg2tcpserver(msg, end = '\n'):
	msg = msg + end
	tcp_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp_cli.connect(('localhost', 30000))
	tcp_cli.send(bytes(msg.encode("ascii")))
# 	buff = tcp_cli.recv(8192)
# 	print(buff)
	tcp_cli.close()

def get_network_cfg():
	with open("/etc/netplan/50-cloud-init.yaml", "r") as fd:
		netplan_cfg = yaml.load(fd)

	return netplan_cfg

default_network_cfg = {
	'network':
		{'ethernets':
			 {'eth0':
				  {'dhcp4': False,
				   'addresses': ['192.168.101.100/24'],
				   'gateway4': '192.168.101.1',
				   'nameservers':
					   {
						   'addresses': ['114.114.114.114']
					   }
				   }
			  },
		 'version': 2}
}


def revert_ip_netmask(ip_netmask):
	ipv4 = ipaddress.IPv4Interface(f"{ip_netmask}")
	# print(str(ipv4.ip), str(ipv4.netmask))
	return str(ipv4.ip), str(ipv4.netmask)

def convert_ip_netmask(ip, netmask):
	# print(f"{ip}/{netmask}")
	ipv4 = ipaddress.IPv4Interface(f"{ip}/{netmask}")
	# print(ipv4.with_prefixlen)
	return ipv4.with_prefixlen

def set_network(network_config):
	default_network_cfg = get_network_cfg()
	default_network_cfg["network"]["ethernets"]["eth0"]["addresses"][0] = convert_ip_netmask(network_config['ip'], network_config['netmask'])
	default_network_cfg["network"]["ethernets"]["eth0"]["gateway4"] = network_config["gateway"]
	default_network_cfg["network"]["ethernets"]["eth0"]["nameservers"]["addresses"][0] = network_config["dns"]

	with open("/etc/netplan/50-cloud-init.yaml", "w+") as fd:
		yaml.dump(default_network_cfg, fd)

	os.system("sudo netplan apply")

# network_config = {"network": {
#     "ip": "192.168.101.13",
#     "netmask": "255.255.255.0",
#     "gateway": "192.168.101.1",
#     "dns": "114.114.114.114"
#   },}
#
# set_network(network_config["network"])

def get_db37_cmd(config):
	cmd = f"CONF:db37 {config['address']} {config['enable']} {config['enable']} {config['output']} {config['trigger_edge']} {config['trigger_enable']} {config['msb_level']} {config['data_level']}"
	return cmd

def get_db25_cmd(config, port):
	print(config)
	cmd = f"CONF:db25:{port} {config['address']} {config['enable']} {config['output']} {config['msb_level']} {config['data_level']}"
	return cmd

def get_trig_r_cmd(config, option):
	cmd = f"CONF:trig_r:{option} {config['trigger_enable']} {config['trigger_level']} {config['output']} {config['r_enable']} {config['r_enable']}"
	return cmd

def get_pos_trig_in_cmd(config):
	cmd = f"CONF:pos_trig_in {config['r_enable']} {config['r_trig_edge']}"
	return cmd

# send_msg2tcpserver(get_pos_trig_in_cmd(""))
