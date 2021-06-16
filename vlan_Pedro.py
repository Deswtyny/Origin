#!/usr/bin/env python
from sys import exit

from mininet.node import Host
from mininet.topo import Topo, SingleSwitchTopo, LinearTopo
from mininet.util import quietRun
from mininet.log import error, setLogLevel


class VLANHost( Host ):

    def config( self, vlan=100, **params ):

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        newName = '%s.%d' % ( intf, vlan )
        intf.name = newName
        self.nameToIntf[ newName ] = intf

        return r


hosts = { 'vlan': VLANHost }


def exampleAllHosts( vlan ):
    host = partial( VLANHost, vlan=vlan )

    topo = SingleSwitchTopo( k=2 )
    net = Mininet( host=host, topo=topo, waitConnected=True )
    net.start()
    CLI( net )
    net.stop()


class VLANStarTopo( LinearTopo ):

    def build( self, k=2, n=2, vlanBase=100 ):
        s1 = self.addSwitch( 's1' )
        for i in range( k ):
            vlan = vlanBase + i
            for j in range(n):
                name = 'h%d-%d' % ( j+1, vlan )
                h = self.addHost( name, cls=VLANHost, vlan=vlan )
                self.addLink( h, s1 )
        for j in range( n ):
            h = self.addHost( 'h%d' % (j+1) )
            self.addLink( h, s1 )


def exampleCustomTags():

    net = Mininet( topo=VLANStarTopo(), waitConnected=True )
    net.start()
    CLI( net )
    net.stop()


if __name__ == '__main__':
    import sys
    from functools import partial

    from mininet.net import Mininet
    from mininet.cli import CLI

    setLogLevel( 'info' )

    if not quietRun( 'which vconfig' ):
        error( "Cannot find command 'vconfig'\nThe package",
               "'vlan' is required in Ubuntu or Debian,",
               "or 'vconfig' in Fedora\n" )
        exit()

    if len( sys.argv ) >= 2:
        exampleAllHosts( vlan=int( sys.argv[ 1 ] ) )
    else:
        exampleCustomTags()
