terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.57.0"
    }
  }
  required_version = ">= 1.14.1"

  backend "azurerm" {
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = local.resource_group_name
  location = "westeurope"
}

resource "azurerm_storage_account" "st_func" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "sc_func" {
  name                  = "myfunction"
  storage_account_id    = azurerm_storage_account.st_func.id
  container_access_type = "private"
}

resource "azurerm_service_plan" "func_plan" {
  name                = local.service_plan_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "FC1"
}

resource "azurerm_function_app_flex_consumption" "func" {
  name                = local.function_app_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.func_plan.id

  storage_container_type      = "blobContainer"
  storage_container_endpoint  = "${azurerm_storage_account.st_func.primary_blob_endpoint}${azurerm_storage_container.sc_func.name}"
  storage_authentication_type = "StorageAccountConnectionString"
  storage_access_key          = azurerm_storage_account.st_func.primary_access_key

  https_only                                     = true
  webdeploy_publish_basic_authentication_enabled = false

  runtime_name           = "python"
  runtime_version        = "3.13"
  maximum_instance_count = 40
  instance_memory_in_mb  = 512

  app_settings = {
    STORAGE_ACCOUNT_NAME                        = azurerm_storage_account.st_func.name
    STORAGE_TABLE_NAME                          = azurerm_storage_table.st_tbl_records.name
    # PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY = true
  }
  identity {
    type = "SystemAssigned"
  }
  site_config {
    minimum_tls_version                    = "1.3"
    application_insights_connection_string = azurerm_application_insights.appi.connection_string
  }
  lifecycle {
    ignore_changes = [
      app_settings["WEBSITE_ENABLE_SYNC_UPDATE_SITE"],
      app_settings["WEBSITE_RUN_FROM_PACKAGE"],
      tags["hidden-link: /app-insights-conn-string"],
      tags["hidden-link: /app-insights-instrumentation-key"],
      tags["hidden-link: /app-insights-resource-id"],
    ]
  }
}


resource "azurerm_log_analytics_workspace" "logs" {
  name                = local.log_analytics_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "appi" {
  name                = local.app_insights_name
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
  principal_id         = azurerm_function_app_flex_consumption.func.identity[0].principal_id
}

output "function_app_name" {
  value = azurerm_function_app_flex_consumption.func.name
}

resource "random_string" "random" {
  length  = 8
  special = false
  upper   = false
  lower   = true
  numeric = false
}

locals {
  unique_name = random_string.random.result

  # Resource name locals built from the unique_name prefix (match existing naming patterns)
  resource_group_name   = "rg-${local.unique_name}"
  storage_function_name = "stfunc${local.unique_name}"
  log_analytics_name    = "log-${local.unique_name}"
  app_insights_name     = "appi-${local.unique_name}"
  service_plan_name     = "app-service-plan-${local.unique_name}"
  function_app_name     = "func-${local.unique_name}"
  storage_account_name  = lower("${local.unique_name}sa")

}