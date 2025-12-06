terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 4.55.0"
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
  name     = "rg-azfunc-python"
  location = "westeurope"
}

resource "azurerm_storage_account" "st_func" {
  name                     = "stfuncpython26167"
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
  name                = "plan-func-python-deployment-26167"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "FC1"
}

resource "azurerm_function_app_flex_consumption" "func" {
  name                = "func-python-26167"
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
  runtime_version        = "3.11"
  maximum_instance_count = 40
  instance_memory_in_mb  = 512

  app_settings = {
    # https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings#python_enable_worker_extensions
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"

    STORAGE_ACCOUNT_NAME = azurerm_storage_account.st_func.name
    STORAGE_TABLE_NAME   = azurerm_storage_table.st_tbl_records.name

    # https://learn.microsoft.com/en-us/troubleshoot/azure/azure-monitor/app-insights/telemetry/opentelemetry-troubleshooting-python#duplicate-trace-logs-in-azure-functions
    # ### Duplicate trace logs in Azure Functions ###
    # If you see a pair of entries for each trace log within Application Insights, you probably enabled the following types of logging instrumentation:
    # The native logging instrumentation in Azure Functions
    # The azure-monitor-opentelemetry logging instrumentation within the distribution
    # To prevent duplication, you can disable the distribution's logging, but leave the native logging instrumentation in Azure Functions enabled. To do this, set the OTEL_LOGS_EXPORTER environment variable to None.
    OTEL_LOGS_EXPORTER = "None"
    # https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration?tabs=python#set-the-cloud-role-name-and-the-cloud-role-instance
    OTEL_SERVICE_NAME        = "MyFunctionApp"
    OTEL_RESOURCE_ATTRIBUTES = "service.instance.id=MyFunctionApp"
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
  name                = "logs-func-python-26167"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "appi" {
  name                = "appi-func-python-26167"
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