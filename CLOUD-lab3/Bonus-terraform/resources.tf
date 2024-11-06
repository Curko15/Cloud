resource "azurerm_resource_group" "resource_group" {
  # TODO: resource group code here.
}

resource "azurerm_kubernetes_cluster" "aks_cluster" {
  # TODO: cluster code here.


  # Don't worry about the code below.
  identity {
    type = "SystemAssigned"
  }

  linux_profile {
    admin_username = "azureadmin"

    ssh_key {
      key_data = jsondecode(azapi_resource_action.ssh_public_key_gen.output).publicKey
    }
  }
}
