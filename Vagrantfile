# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "debian-wheezy64"
    config.vm.box_url = "https://dl.dropboxusercontent.com/s/xymcvez85i29lym/vagrant-debian-wheezy64.box"

    config.vm.hostname = "lxc"
    config.vm.provision :shell, :path => "append_authorized_keys_to_root.sh"

    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true
    config.hostmanager.ignore_private_ip = false
    config.hostmanager.include_offline = true
    config.vm.network :private_network, ip: "192.168.33.10"
    config.hostsupdater.aliases = ["lxc.example.com"]
    config.hostmanager.aliases = ["lxc.example.com"]
end
