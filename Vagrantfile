# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # ubuntu 14.04 image
  config.vm.box = "modcloth/trusty64"
  # setup script for vagrant and travis
  config.vm.provision "shell", path: "scripts/setup.sh"
  # setup postgres script for vagrant
  config.vm.provision "shell", path: "scripts/postgres.sh"
  # setup tomita script for vagrant
  config.vm.provision "shell", path: "scripts/tomita_vagrant.sh"
end
