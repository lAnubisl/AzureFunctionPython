terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.45.0"
    }
  }
  required_version = ">= 1.4.6"

  backend "azurerm" {
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-func-python-deployment-test"
  location = "westeurope"
}

resource "azurerm_storage_account" "st_func" {
  name                     = "stfuncpython13876"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_service_plan" "func_plan" {
  name                = "plan-func-python-deployment-13876"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_linux_function_app" "func" {
  name                       = "func-python-13876"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.st_func.name
  storage_account_access_key = azurerm_storage_account.st_func.primary_access_key
  builtin_logging_enabled    = false
  app_settings = {
    AzureWebJobsFeatureFlags = "EnableWorkerIndexing"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    FUNCTIONS_WORKER_RUNTIME = "python"
    STORAGE_ACCOUNT_NAME     = azurerm_storage_account.st_func.name
    STORAGE_TABLE_NAME       = azurerm_storage_table.st_tbl_records.name
  }
  identity {
    type = "SystemAssigned"
  }
  site_config {
    application_insights_connection_string = azurerm_application_insights.appi.connection_string
    application_stack {
      python_version = "3.11"
    }
  }
}

resource "azurerm_log_analytics_workspace" "logs" {
  name                = "logs-func-python-13876"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "appi" {
  name                = "appi-func-python-13876"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.logs.id
  application_type    = "other"
  retention_in_days   = 30
}

resource "azurerm_storage_table" "st_tbl_records" {
  name                 = "records"
  storage_account_name = azurerm_storage_account.st_func.name
}

resource "azurerm_role_assignment" "table_func_role_assignment" {
  scope                = azurerm_storage_account.st_func.id
  role_definition_name = "Storage Table Data Contributor"
  principal_id         = azurerm_linux_function_app.func.identity[0].principal_id
}
