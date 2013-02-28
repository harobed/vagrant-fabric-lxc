# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "DebianSqueeze64"
  config.vm.box_url = "http://dl.dropbox.com/u/937870/VMs/squeeze64.box"
  config.vm.provision :shell, :path => "append_authorized_keys_to_root.sh"
  config.vm.provision :shell, :inline => "sysctl net.ipv4.ip_forward=1; iptables -t nat -F POSTROUTING; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; ifup br0"
  config.vm.host_name = "vagrant.example.com"
  config.hosts.name = "vagrant.example.com"
  config.hosts.aliases = "example.com"

  config.vm.network :hostonly, "192.168.33.10", :mac => "080027e5f699"

  #config.vm.forward_port 80, 8080
end
