// Parameters
@description('Location for the resources')
param location string = resourceGroup().location

@description('Council name to be appended to resource names')
param councilName string

@description('Name for the Speech service')
param speechServiceName string = toLower('lrgspeech${councilName}')

@description('SKU for the Speech service')
@allowed([
  'Free'
  'S0'
])
param speechSkuName string = 'S0'

@description('Name for the App Service')
param appServiceName string = toLower('lrgappservice${councilName}')

@description('SKU for the App Service')
@allowed([
  'F1'
  'B1'
])
param appServiceSkuName string = 'B1'

@description('Name for the Azure Cognitive Search service. Must be between 2 and 60 characters, using lowercase letters, digits, or dashes.')
@minLength(2)
@maxLength(60)
param searchServiceName string = toLower('lrgsearch${councilName}')

@description('Pricing tier for the Azure Cognitive Search service.')
@allowed([
  'free'
  'basic'
])
param searchSku string = 'basic'

@description('Number of replicas for the Azure Cognitive Search service.')
@minValue(1)
@maxValue(2)
param replicaCount int = 1

@description('Number of partitions for the Azure Cognitive Search service.')
@allowed([
  1
  2
])
param partitionCount int = 1

// Variables
@description('Dynamic Storage Account Name')
var storageAccountName = toLower('sa${councilName}lrg01')

// Ensure the storage account name is within the length limit
var truncatedStorageAccountName = take(storageAccountName, 24)

// Dictionary to map SKU names to tiers
var skuToTier = {
  F1: 'Free'
  B1: 'Basic'
}

@description('Tier for the App Service Plan')
var appServicePlanTier = skuToTier[appServiceSkuName]

// Resources

// Speech Service Resource
resource speechService 'Microsoft.CognitiveServices/accounts@2022-12-01' = {
  name: speechServiceName
  location: location
  kind: 'SpeechServices'
  sku: {
    name: speechSkuName
  }
  properties: {
    apiProperties: {
      customVoiceEnabled: true
    }
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2021-02-01' = {
  name: '${appServiceName}plan'
  location: location
  sku: {
    name: appServiceSkuName
    tier: appServicePlanTier
  }
  properties: {
    reserved: true
  }
}

// Python App Service
resource pythonAppService 'Microsoft.Web/sites@2021-02-01' = {
  name: '${appServiceName}-python'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.8'
    }
  }
}

// React App Service
resource reactAppService 'Microsoft.Web/sites@2021-02-01' = {
  name: '${appServiceName}-react'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
    }
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: truncatedStorageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

// Blob Services
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2021-02-01' = {
  name: 'default'
  parent: storageAccount
}

// Storage Container
resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-02-01' = {
  name: 'data'
  parent: blobService
}

// Azure Cognitive Search Resource
resource searchService 'Microsoft.Search/searchServices@2020-08-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: searchSku
  }
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
  }
}
