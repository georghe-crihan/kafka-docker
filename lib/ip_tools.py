import socket
from random import shuffle

def _address_family(address):
    """
        Attempt to determine the family of an address (or hostname)
        :return: either socket.AF_INET or socket.AF_INET6 or socket.AF_UNSPEC if the address family
                 could not be determined
    """
    if address.startswith('[') and address.endswith(']'):
        return socket.AF_INET6
    for af in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(af, address)
            return af
        except (ValueError, AttributeError, socket.error):
            continue
    return socket.AF_UNSPEC

def get_ip_port_afi(host_and_port_str):
    """
        Parse the IP and port from a string in the format of:
            * host_or_ip          <- Can be either IPv4 address literal or hostname/fqdn
            * host_or_ipv4:port   <- Can be either IPv4 address literal or hostname/fqdn
            * [host_or_ip]        <- IPv6 address literal
            * [host_or_ip]:port.  <- IPv6 address literal
        .. note:: IPv6 address literals with ports *must* be enclosed in brackets
        .. note:: If the port is not specified, default will be returned.
        :return: tuple (host, port, afi), afi will be socket.AF_INET or socket.AF_INET6 or socket.AF_UNSPEC
    """
    host_and_port_str = host_and_port_str.strip()
    if host_and_port_str.startswith('['):
        af = socket.AF_INET6
        host, rest = host_and_port_str[1:].split(']')
        if rest:
            port = int(rest[1:])
        else:
            port = DEFAULT_KAFKA_PORT
        return host, port, af
    else:
        if ':' not in host_and_port_str:
            af = _address_family(host_and_port_str)
            return host_and_port_str, DEFAULT_KAFKA_PORT, af
        else:
            # now we have something with a colon in it and no square brackets. It could be
            # either an IPv6 address literal (e.g., "::1") or an IP:port pair or a host:port pair
            try:
                # if it decodes as an IPv6 address, use that
                socket.inet_pton(socket.AF_INET6, host_and_port_str)
                return host_and_port_str, DEFAULT_KAFKA_PORT, socket.AF_INET6
            except AttributeError:
                log.warning('socket.inet_pton not available on this platform.'
                            ' consider pip install win_inet_pton')
                pass
            except (ValueError, socket.error):
                # it's a host:port pair
                pass
            host, port = host_and_port_str.rsplit(':', 1)
            port = int(port)

            af = _address_family(host)
            return host, port, af

def collect_hosts(hosts, randomize=True):
    """
    Collects a comma-separated set of hosts (host:port) and optionally
    randomize the returned list.
    """

    if isinstance(hosts, basestring):
        hosts = hosts.strip().split(',')

    result = []
    afi = socket.AF_INET
    for host_port in hosts:

        host, port, afi = get_ip_port_afi(host_port)

        if port < 0:
            port = DEFAULT_KAFKA_PORT

        result.append((host, port, afi))

    if randomize:
        shuffle(result)

    return result

