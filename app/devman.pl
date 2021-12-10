#!/usr/bin/env perl
use utf8;
use strict;
use warnings;

use JSON;
use SNMP::Info;

main();

sub main {
    die
      "Invalid number of arguments. You should have passed just one IP address."
      if ( $#ARGV != 0 );
    my $ip = $ARGV[0];
    die "Invalid IP address: $ip" if !( check_ip($ip) );
    my $json = get_snmp_info($ip);
    print("$json\n");
}

sub get_snmp_info {
    my ($ip) = @_;

    my $community =
      defined $ENV{SNMP_COMMUNITY} ? $ENV{SNMP_COMMUNITY} : 'public';

    my $info = new SNMP::Info(
        AutoSpecify => 1,
        Debug       => 0,
        DestHost    => $ip,
        Community   => $community,
        Version     => 2,
    ) or die("Could not connect to $ip");

    my $err = $info->error();
    die("$err") if defined $err;

    # We'll store all the SNMP info here
    my %ports_info;

    # A list of interface-ids (iid)
    my $interfaces = $info->interfaces();

    # VLAN numbers
    my $vlans_nums = $info->i_vlan_membership();

    # Port description
    my $ports_desc = $info->i_alias();

    # Port type. Unfortunately, it doesn't always get it right.
    # Needed for port type filtration.
    my $ports_type = $info->i_type();

    # Port Speed
    my $ports_speed = $info->i_speed();

    # Physical Port State
    my $ports_status_phys = $info->i_up();

    # Administrative Port State
    my $ports_status_admin = $info->i_up_admin();

    # PVID
    # We need two of them as the end result depends on a specific device model
    my $ports_vlan_pvid1 = $info->i_vlan();
    my $ports_vlan_pvid2 = $info->i_vlan2();

    foreach my $iid ( keys %$interfaces ) {

        # Filtering out non-physical interfaces.
        next unless ( $ports_type->{$iid} =~ /ethernetCsmacd|gigabitEthernet/ );
        next
          if ( $interfaces->{$iid} =~
            /Embedded-Service-Engine|Vlan|cmif0|enif0|swif0/ );

       # Zyxels number their ports starting from 0, whereas their CLI uses [1; ]
        if ( $interfaces->{$iid} =~ m/swp\d+/ ) {
            $interfaces->{$iid} =~ s/swp//;
            $interfaces->{$iid} = $interfaces->{$iid} + 1;
        }

        # Interface ID is an internal interface number exposed only via SNMP
        my $temp_sys_name = $interfaces->{$iid};
        $ports_info{$temp_sys_name}{'iid'} = $iid;

        # System Port Name (e.g. FastEthernet0/1)
        $ports_info{$temp_sys_name}{'port_sys_name'} = $interfaces->{$iid};

        # VLANs assigned to a port
        $ports_info{$temp_sys_name}{'vlan_num'} = '';
        if ( defined $vlans_nums->{$iid} ) {
            $ports_info{$temp_sys_name}{'vlan_num'} = join ', ',
              sort { $a <=> $b } @{ $vlans_nums->{$iid} };
        }

        # Port Description
        $ports_info{$temp_sys_name}{'port_desc'} = $ports_desc->{$iid};

        # Port Type
        $ports_info{$temp_sys_name}{'port_type'} = $ports_type->{$iid};

        # Port Speed
        $ports_info{$temp_sys_name}{'port_speed'} = $ports_speed->{$iid};

        # Physical Port State
        $ports_info{$temp_sys_name}{'port_status_phys'} =
          $ports_status_phys->{$iid};

        # Administrative Port State
        $ports_info{$temp_sys_name}{'port_status_admin'} =
          $ports_status_admin->{$iid};

        # PVID
        $ports_info{$temp_sys_name}{'pvid'} = '';
        if ( exists( $ports_vlan_pvid1->{$iid} ) ) {
            $ports_info{$temp_sys_name}{'pvid'} = $ports_vlan_pvid1->{$iid};
        }
        elsif ( exists( $ports_vlan_pvid2->{$iid} ) ) {
            $ports_info{$temp_sys_name}{'pvid'} = $ports_vlan_pvid2->{$iid};
        }
    }

    return encode_json \%ports_info;
}

sub check_ip {
    my ($ip) = @_;
    return $ip =~ m/^[1-9][0-9]{0,2}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
}
