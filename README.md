# cloudify-nsx-t-plugin

Cloudify NSX-T Plugin enables users create NSX-T Resources in NSX-T manager that can be exposed to the vsphere environment

The plugin provides the following features for interacting with NSX-T API:
1. Segment:
   - Create Segment
   - Delete Segment
   
2. DHCP Server Config:
   - Create DHCP Server Config
   - Delete DHCP Server Config
 
3. Tier1 Gateway:
   - Create Tier1 Gateway
   - Delete Tier1 Gateway

## Authentication with NSX-T

Each node template, has a `client_config` property which stores your account credentials.

The `client_config` consists of the following:
- `host`: _Required_.: Your NSX-T Manager Host IP.
- `port`: _Required_.: Your NSX-T Manager Port that listen on.
- `username`: _Required_.: Your NSX-T Manager Username.
- `password`: _Required_.: Your NSX-T Manager Password.
- `auth_type`: Authentication Type. It supports the following:
    - `basic`: Default value.
    - `session`  
- `insecure`: If true, SSL validation is skipped. Default `false`.
- `cert`: Your cert file path.

```yaml
dsl_definitions:

  client_config: &client_config
    host: { get_input: host }
    port: { get_input: port }
    username: { get_input: username }
    password: { get_input: password }
``` 

## Common Properties

Openstack Plugin node types have these common properties, except where noted:

**Properties**

  * `client_config`: A dictionary that contains values to be passed to the connection client.
  * `resource_config`: A dictionary with required and common parameters to the resource's create or put call.

## Common Runtime Properties

Node instances of any of the types defined in this plugin are set with the following runtime properties during the `cloudify.interfaces.lifecycle.create operation`:

* `id`: The ID of the NSX-T resource
* `name`: The name of the NSX-T resource
* `type`: The type of the NSX-T resource
* `resource_config`: The resource configuration returned from resource creation

 
## Node Types

### **cloudify.nodes.nsx-t.DhcpServerConfig**

This node type refers to a DHCP Server Config.

**Resource Config**

  * `id`: _String_. _Required_. This is the ID of the DHCP Server Config
  * `display_name`: _String_. _Not required_. The name of DHCP Server Config. if not provided, it will take the same ID value.
  * `description`: _String_. _Not required_. The resource  description.
  * `edge_cluster_path`: _String_. Edge cluster path
  * `lease_time`: _Integer_. IP address lease time in seconds.
  * `server_addresses`: _List_: DHCP server address in CIDR format. Both IPv4 and IPv6 address families are supported.
  * `preferred_edge_paths`: _List_: Edge node path policy paths to edge nodes on which the DHCP servers run.
  * `children`: _List_: subtree for this type within policy tree containing nested elements.
  * `tags`: _List_: Opaque identifiers meaningful to the API user by having pairs of scope and tag.


### DHCP Server Config Example

```yaml
  dhcb_server_config:
    type: cloudify.nodes.nsx-t.DhcpServerConfig
    properties:
      client_config:
        host: { get_input: host }
        port: { get_input: port }
        username: { get_input: username }
        password: { get_input: password }
      resource_config:
        id: test_dhcp_server
        display_name: Test DHCP Server
        description: Test DHCP Server Config
        edge_cluster_path: /infra/sites/default/enforcement-points/default/edge-clusters/272cfe43-ebcc-49bb-8471-62a261ed8931
        tags:
         - scope: Name
           tag: Test DHCP
```

### **cloudify.nodes.nsx-t.Segment**

This node type refers to a Segment.

  * `id`: _String_. _Required_. This is the ID of the Segment
  * `display_name`: _String_. _Not required_. The name of Segment. if not provided, it will take the same ID value.
  * `description`: _String_. _Not required_. The Segment description.
  * `subnet`: _Dict_: Segment Subnet Configuration. The following keys are part of `subnet`:
     - `ip_v4_config`: _Dict_:  IP V4 Configuration.
        - `dhcp_config`: _Dict_: The DHCP Configuration
          - `resource_type`: _String_: Type of the DHCP Configuration. Default: SegmentDhcpV4Config
          - `server_address`: _List_:  IP address of the DHCP server in CIDR format.
          - `dns_servers`: _List_: IP address of DNS servers for subnet.
          - `lease_time`: _Integer_: DHCP lease time for subnet
          - `option`: _Dict_: DHCP options.
        - `gateway_address`: _String_: Gateway IP address in CIDR format IPv4
        - `dhcp_ranges`: DHCP address ranges are used for dynamic IP allocation. Supports address range and CIDR formats. 
     - `ip_v6_config`: _Dict_:  IP V6 Configuration.
                - `dhcp_config`: _Dict_: The DHCP Configuration
          - `resource_type`: _String_: Type of the DHCP Configuration. Default: SegmentDhcpV4Config
          - `server_address`: _List_:  IP address of the DHCP server in CIDR format.
          - `dns_servers`: _List_: IP address of DNS servers for subnet.
          - `lease_time`: _Integer_: DHCP lease time for subnet
          - `option`: _Dict_: DHCP options.
        - `gateway_address`: _String_: Gateway IP address in CIDR format IPv6
        - `dhcp_ranges`: DHCP address ranges are used for dynamic IP allocation. Supports address range and CIDR formats. 
   
  * `admin_state`: _String_. Represents Desired state of the Segment. It supports the following values:
     - `UP`: Default value
     - `Down`
  * `replication_mode`: _String_. Replication mode of the Segment. If this field is not set for overlay segment then the default of `MTEP` will be used. It supports the following values:
     - `MTEP`
     - `SOURCE`
  * `transport_zone_path`: _String_: Policy path to the transport zone.
  * `connectivity_path`: _String_: Policy path to the connecting Tier-0 or Tier-1.
  * `dhcp_config_path`: _String_: Policy path to DHCP server or relay configuration to use for all IPv4 & IPv6 subnets configured on this segment.
  * `l2_extension`: _Dict_: Configuration for extending Segment through L2 VPN.
  * `domain_name`: _String_: DNS domain name.
  * `extra_configs`: _List_: Extra configs on Segment. This property could be used for vendor specific configuration in key value string pairs, the setting in extra_configs will be automatically inheritted by segment ports in the Segment
  * `metadata_proxy_paths`: _List_: Metadata Proxy Configuration Paths.
  * `mac_pool_id`: _String_: Allocation mac pool associated with the Segment, Mac pool id that associated with a Segment.
  * `overlay_id`: _String_: Overlay connectivity ID for this Segment Used for overlay connectivity of segments.
  * `tags`: _List_: Opaque identifiers meaningful to the API user by having pairs of scope and tag.
  * `children`: _List_: subtree for this type within policy tree containing nested elements.
  * `address_bindings`: _List_: Address bindings for the Logical switch. Array of PacketAddressClassifier https://vdc-download.vmware.com/vmwb-repository/dcr-public/9e1c6bcc-85db-46b6-bc38-d6d2431e7c17/30af91b5-3a91-4d5d-8ed5-a7d806764a16/api_includes/types_PacketAddressClassifier.html
  * `bridge_profiles`: _List_: Bridge Profile Configuration Multiple distinct L2 bridge profiles can be configured.
  * `advanced_config`: _Dict_: Advanced configuration for Segment.
  * `vlan_ids`: _List_: VLAN ids for VLAN backed Segment. Can be a VLAN id or a range of VLAN ids specified with '-' in between.
      

**Relationships**
  * `cloudify.relationships.nsx-t.segment_connected_to_dhcp_server_config`:
    * `cloudify.nodes.nsx-t.DhcpServerConfig`: Depend on DHCP Server Config


### Segment Example

```yaml
  segment:
    type: cloudify.nodes.nsx-t.Segment
    properties:
      client_config:
        host: { get_input: host }
        port: { get_input: port }
        username: { get_input: username }
        password: { get_input: password }
      resource_config:
          id: test_segment
          display_name: test-segment
          description: Test Segment Config
          transport_zone_path: /infra/sites/default/enforcement-points/default/transport-zones/1b3a2f36-bfd1-443e-a0f6-4de01abc963e
          connectivity_path: /infra/tier-1s/test-tier1
          dhcp_config_path: /infra/dhcp-server-configs/test_dhcp_server
          subnet:
            ip_v4_config:
              dhcp_config:
                server_address: 192.168.11.11/24
                lease_time: 86400
                resource_type: SegmentDhcpV4Config
              gateway_address: 192.168.11.12/24
              dhcp_ranges:
                - "192.168.11.100-192.168.11.160"
            ip_v6_config:
              dhcp_config:
                server_address: fc7e:f206:db42::6/48
                lease_time: 86400
                resource_type: SegmentDhcpV6Config
              gateway_address: fc7e:f206:db42::2/48   
    relationships:
      - type: cloudify.relationships.nsx-t.segment_connected_to_dhcp_server_config
        target: dhcb_server_config
```

### **cloudify.nodes.nsx-t.Tier1**

This node type refers to a Tier1 Gateway.

**Resource Config**

  * `id`: _String_. _Required_. This is the ID of the Tier1 Gateway
  * `display_name`: _String_. _Not required_. The name of Tier1 Gateway. if not provided, it will take the same ID value.
  * `tier0_path`: _String_. _Not required_. Specify Tier-1 connectivity to Tier-0 instance.
  * `type`: _String_. Tier1 connectivity type for reference.
  * `dhcp_config_paths`: _List_. DHCP configuration for Segments connected to Tier-1
  * `disable_firewall`: _Boolean_: Disable or enable gateway firewall. Default False
  * `enable_standby_relocation`: _Boolean_: Flag to enable standby service router relocation.
  * `failover_mode`: _String_: Determines the behavior when a Tier-1 instance restarts after a failure. Default NON_PREEMPTIVE
  * `intersite_config`: _Dict_: Inter site routing configuration when the gateway is streched.
     * `fallback_sites`: _List_: Fallback site to be used as new primary site on current primary site failure.
     * `intersite_transit_subnet`: _String_: IPv4 subnet for inter-site transit segment connecting service routers across sites for stretched gateway. Default `169.254.32.0/20`
     * `last_admin_active_epoch`: _Integer_: Epoch(in seconds) is auto updated based on system current timestamp when primary locale service is updated
     * `primary_site_path`: _String_: Primary egress site for gateway.
  * `ipv6_profile_paths`: _List_: Configuration IPv6 NDRA and DAD profiles . Either or both NDRA and/or DAD profiles can be configured.
  * `pool_allocation`: _String_: Supports edge node allocation at different sizes for routing and load balancer service to meet performance and scalability requirements. Default ROUTING
  * `qos_profile`: _Dict_: QoS Profile configuration for Tier1 router link connected to Tier0 gateway.
     * `egress_qos_profile_path`: _String_: Policy path to gateway QoS profile in egress direction.
     * `ingress_qos_profile_path`: _String_: Policy path to gateway QoS profile in ingress direction.
  * `route_advertisement_rules`: _List_: Route advertisement rules and filtering.
  * `route_advertisement_types`: _List_: Enable different types of route advertisements.
  * `children`: _List_: subtree for this type within policy tree containing nested elements.
  * `tags`: _List_: Opaque identifiers meaningful to the API user


### Tier1 Example  

```yaml
  tier1:
    type: cloudify.nodes.nsx-t.Tier1
    properties:
      client_config:
        host: { get_input: host }
        port: { get_input: port }
        username: { get_input: username }
        password: { get_input: password }
      resource_config:
          id: test_tier1
          display_name: Test Tier1 Router
          description: Test Tier1 Router
          tier0_path:{ get_input: tier0_path }
```

Note: The configuration for the above resources are based on the NSX-T API documentation:
   1. https://vdc-download.vmware.com/vmwb-repository/dcr-public/9e1c6bcc-85db-46b6-bc38-d6d2431e7c17/30af91b5-3a91-4d5d-8ed5-a7d806764a16/api_includes/policy_networking_connectivity_segment.html
   2. https://vdc-download.vmware.com/vmwb-repository/dcr-public/9e1c6bcc-85db-46b6-bc38-d6d2431e7c17/30af91b5-3a91-4d5d-8ed5-a7d806764a16/api_includes/policy_networking_ip_management_dhcp_dhcp_server_configs.html
   3. https://vdc-download.vmware.com/vmwb-repository/dcr-public/9e1c6bcc-85db-46b6-bc38-d6d2431e7c17/30af91b5-3a91-4d5d-8ed5-a7d806764a16/api_includes/policy_networking_connectivity_tier-1_gateways_tier-1_gateways.html
