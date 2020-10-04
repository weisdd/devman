# devman

## General description

DevMan was built in a few days to give our technical (or not so technical) personnel an access to some information about network devices, specifically:

* a list of devices retrieved from Netbox and their location (=urls) in NetBox, Cacti, and Zabbix;
* configuration (description, VLANs, speed) retrieved via SNMP;
* consistency reports on Zabbix' configuration.

## Important note

The project has never aimed to be something widely deployed, and was developed with the assumptions made to fit the current IT landscape of one of the companies I work for. It still requires a lot of changes in terms of UX, tests, documentation, and maintainability, so don't expect it to be a perfect solution. Though, in our environment, it serves its purpose really well.

All the changes mentioned above are yet to come true.

## Docker Image

<https://quay.io/repository/weisdd/devman?tab=tags>
