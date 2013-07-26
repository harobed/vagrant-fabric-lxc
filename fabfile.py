from fabric.api import task, local, run, env, put, settings, hide
from fabric.contrib.files import append as append_to_file
import fabtools  # NOQA


def _settings_dict(config):
    settings = {}  # NOQA

    # Build host string
    settings['user'] = config['User']
    settings['hosts'] = [config['HostName']]
    settings['port'] = config['Port']

    # Strip leading and trailing double quotes introduced by vagrant 1.1
    settings['key_filename'] = config['IdentityFile'].strip('"')

    settings['forward_agent'] = (config.get('ForwardAgent', 'no') == 'yes')
    settings['disable_known_hosts'] = True

    return settings


def ssh_config(name=''):
    """
    Get the SSH parameters for connecting to a vagrant VM.
    """
    with settings(hide('running')):
        output = local('vagrant ssh-config %s' % name, capture=True)  # NOQA

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
    return
    fabtools.require.deb.packages([
        'lxc', 'debootstrap', 'bridge-utils', 'libvirt-bin', 'dnsmasq'
    ])
    append_to_file(
        '/etc/fstab',
        'cgroup /sys/fs/cgroup cgroup defaults 0 0'
    )
    run('mount /sys/fs/cgroup')
    put(
        'templates/lxc-squeeze-custom',
        '/usr/lib/lxc/templates/'
    )
    run('chmod ugo+x /usr/lib/lxc/templates/lxc-squeeze-custom')
    append_to_file(
        '/etc/network/interfaces',
        """\

auto br0
iface br0 inet static
   address 192.168.10.254
   netmask 255.255.255.0
   bridge_ports none
   bridge_stp on
   bridge_fd 1
   bridge_maxwait 0
   up iptables -t nat -F POSTROUTING
   up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
"""
    )

    run('sysctl net.ipv4.ip_forward=1')
    append_to_file(
        '/etc/sysctl.conf',
        'net.ipv4.ip_forward=1'
    )
    run('ifup br0')

    append_to_file(
        '/etc/dnsmasq.conf',
        """\
interface=br0
dhcp-range=192.168.10.1,192.168.10.250,12h
dhcp-option=3,192.168.10.254
"""
    )
    run('echo "nameserver 8.8.8.8" > /etc/resolv.conf')
    run('/etc/init.d/dnsmasq restart')


@task
def create_container():
    run('lxc-create -n my_container -t squeeze-custom')


@task
def destroy_container():
    pass
