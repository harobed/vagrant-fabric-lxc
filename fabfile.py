import textwrap
from fabric.api import task, local, run, env, put, settings, hide, shell_env
from fabric.contrib.files import append as append_to_file
from fabric.contrib.files import sed
from fabric.contrib.project import upload_project
import fabtools  # NOQA

lxc_containers = {
    'samplebox': '10.0.0.10',
}


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


def set_timezone(timezone):
    fabtools.utils.run_as_root('echo "%s" > /etc/timezone' % timezone)
    fabtools.utils.run_as_root('dpkg-reconfigure --frontend noninteractive tzdata')
    fabtools.require.service.restarted('cron')


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
def remote():
    env['hosts'] = ['www.hosting.tld']
    env['user'] = 'root'


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'


@task
def update_lxc_template():
    put(
        'assets/lxc/lxc-debian-sk',
        '/usr/share/lxc/templates/'
    )
    run('chmod ugo+x /usr/share/lxc/templates/lxc-debian-sk')


@task
def requirements():
    fabtools.deb.update_index()
    fabtools.deb.upgrade()
    fabtools.require.deb.nopackages(['bind9', 'bind9-host'])
    fabtools.require.deb.packages([
        'lxc', 'debootstrap', 'bridge-utils', 'libvirt-bin',
        'dnsmasq', 'rsync', 'fail2ban', 'vim', 'mc', 'ntpdate',
        'fail2ban'
    ])
    set_timezone('Europe/Paris')
    run('ntpdate-debian')


@task
def install():
    requirements()

    append_to_file(
        '/etc/fstab',
        'cgroup /sys/fs/cgroup cgroup defaults 0 0'
    )
    run('mount /sys/fs/cgroup')

    update_lxc_template()

    append_to_file(
        '/etc/network/interfaces',
        textwrap.dedent("""
        auto br0
        iface br0 inet static
        address 10.0.0.254
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
        dhcp-range=10.0.0.1,10.0.0.250,12h
        dhcp-option=3,10.0.0.254
        """)
    )
    run('echo "nameserver 8.8.8.8" > /etc/resolv.conf')
    run('/etc/init.d/dnsmasq restart')

    install_shorewall()
    install_pound()


@task
def install_pound():
    fabtools.require.deb.package('pound')
    with settings(hide('running'), shell_env()):
        sed('/etc/default/pound', 'startup=0', 'startup=1')

    put(
        'assets/pound/pound.cfg',
        '/etc/pound/pound.cfg'
    )

    run('service pound start')


@task
def install_shorewall():
    fabtools.require.deb.package('shorewall')
    upload_project('assets/shorewall/', '/etc/')

    with settings(hide('running'), shell_env()):
        sed('/etc/default/shorewall', 'startup=0', 'startup=1')

    run('shorewall start')


@task
def create_all_container():
    for hostname, ip in lxc_containers.items():
        run(
            'lxc-create -n %s-lxc -t debian-sk -- --ip=%s --gateway=10.0.0.254' %
            (hostname, ip)
        )
        run('lxc-start -n %s-lxc -d' % hostname, pty=False)
