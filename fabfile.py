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
