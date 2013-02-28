from fabric.api import task, run, env, put
from fabric.contrib.files import append as append_to_file
from fabric.contrib.files import sed
from fabtools.vagrant import ssh_config, _settings_dict
from fabric.utils import puts
import fabtools  # NOQA


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'


#@task
#def install_backport():
    #run('apt-get update')
    #run('apt-get upgrade')
    #fabtools.require.files.file(
        #'/etc/apt/preferences.d/lxc',
        #contents="""\
#Package: lxc
#Pin: release a=squeeze-backports
#Pin-Priority: 1000
#"""
    #)
    #fabtools.require.deb.source('lxc', 'http://backports.debian.org/debian-backports', 'squeeze-backports', 'main')

    #fabtools.deb.preseed_package('lxc', {
        #'lxc/directory': ('string', '/var/lib/lxc'),
        #'lxc/shutdown': ('select', '/usr/bin/lxc-halt'),
        #'lxc/title': ('title', ''),
        #'lxc/auto': ('boolean', 'true')
    #})

    #fabtools.require.deb.packages([
        #'lxc', 'debootstrap', 'bridge-utils', 'libvirt-bin'
    #])

    #append_to_file(
        #'/etc/fstab',
        #'cgroup /sys/fs/cgroup cgroup defaults 0 0'
    #)
    #run('mount /sys/fs/cgroup')


@task
def install():
    fabtools.deb.update_index()
    fabtools.deb.upgrade()
    fabtools.require.deb.packages([
        'lxc', 'debootstrap', 'bridge-utils', 'libvirt-bin'
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
    sed(
        '/etc/network/interfaces',
        '#VAGRANT-END',
        """     up iptables -t nat -F POSTROUTING\\n     up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE\\n\\n#VAGRANT-END"""
    )
    append_to_file(
        '/etc/network/interfaces',
        """\
auto br0
iface br0 inet static
   address 192.168.33.11
   netmask 255.255.255.0
   bridge_ports eth1
   bridge_stp off
   bridge_maxwait 0
   post-up /usr/sbin/brctl setfd br0 0
"""
    )

    run('sysctl net.ipv4.ip_forward=1')
    run('iptables -t nat -F POSTROUTING')
    run('iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')
    run('ifup br0')


@task
def create_container():
    run('lxc-create -n my_container -t squeeze-custom')


@task
def destroy_container():
    pass
