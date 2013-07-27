import textwrap
from fabric.api import task, local, run, env, put, settings, hide
from fabric.contrib.files import append as append_to_file
import fabtools  # NOQA


def _settings_dict(config):
    _settings = {}

    # Build host string
    _settings['user'] = config['User']
    _settings['hosts'] = [config['HostName']]
    _settings['port'] = config['Port']

    # Strip leading and trailing double quotes introduced by vagrant 1.1
    _settings['key_filename'] = config['IdentityFile'].strip('"')

    _settings['forward_agent'] = (config.get('ForwardAgent', 'no') == 'yes')
    _settings['disable_known_hosts'] = True

    return _settings


def ssh_config(name=''):
    """
    Get the SSH parameters for connecting to a vagrant VM.
    """
    with settings(hide('running')):
        output = local('vagrant ssh-config %s' % name, capture=True)

    config = {}
    for line in output.splitlines()[1:]:
        key, value = line.strip().split(' ', 2)
        config[key] = value
    return config


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'


@task
def install():
    fabtools.deb.update_index()
    fabtools.deb.upgrade()
    fabtools.require.deb.packages([
        'lxc', 'debootstrap', 'bridge-utils', 'libvirt-bin', 'dnsmasq'
    ])
    append_to_file(
        '/etc/fstab',
        'cgroup /sys/fs/cgroup cgroup defaults 0 0'
    )
    run('mount /sys/fs/cgroup')

    put(
        'templates/lxc-debian-sk',
        '/usr/lib/lxc/templates/'
    )
    run('chmod ugo+x /usr/lib/lxc/templates/lxc-debian-sk')

    append_to_file(
        '/etc/network/interfaces',
        textwrap.dedent("""
        auto br0
        iface br0 inet static
        address 192.168.10.254
        netmask 255.255.255.0
        bridge_ports none
        bridge_stp off
        bridge_fd 0
        bridge_maxwait 5
        up iptables -t nat -F POSTROUTING
        up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        """)
    )

    run('sysctl net.ipv4.ip_forward=1')
    append_to_file(
        '/etc/sysctl.conf',
        'net.ipv4.ip_forward=1'
    )
    run('ifup br0')

    append_to_file(
        '/etc/dnsmasq.conf',
        textwrap.dedent("""
        interface=br0
        dhcp-range=192.168.10.1,192.168.10.250,12h
        dhcp-option=3,192.168.10.254
        """)
    )
    run('echo "nameserver 8.8.8.8" > /etc/resolv.conf')
    run('/etc/init.d/dnsmasq restart')


@task
def create_container(name='container1'):
    run('lxc-create -n %s -t debian-sk' % name)
    run('lxc-start -n %s -d' % name)


@task
def stop_container(name='container1'):
    run('lxc-stop -n %s' % name)
