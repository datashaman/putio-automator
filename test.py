import miniupnpc

upnp = miniupnpc.UPnP()
print dir(upnp)

upnp.discoverdelay = 10
upnp.discover()

upnp.selectigd()

upnp.addportmapping(43000, 'tcp', upnp.lanaddr, 43000, 'testing', '')
