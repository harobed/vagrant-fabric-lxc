# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
if [ ! -d /root/.ssh ]
then
    sudo mkdir /root/.ssh
    sudo cp .ssh/authorized_keys /root/.ssh/
    sudo chown root:root /root/.ssh/authorized_keys
fi
SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.provider "virtualbox" do |v|
      v.memory = 2048
    end
    config.ssh.forward_agent = true
    config.vm.box = "wheezy64-7.2-fr-nfs-common"
    config.vm.box_url = "https://dl.dropboxusercontent.com/s/xymcvez85i29lym/vagrant-debian-wheezy64.box"
    config.vm.hostname = "lxc"
    config.vm.provision :shell, inline: $script
    config.vm.provision :hostmanager
    config.vm.network :private_network, ip: "192.168.33.10"
    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true
    config.hostmanager.ignore_private_ip = false
    config.hostmanager.include_offline = true
    config.hostmanager.aliases = ["lxc.example.com"]
end

