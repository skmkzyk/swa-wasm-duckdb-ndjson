param name string
param location string
param tags object = {}

@description('The SKU of the Static Web App')
@allowed([
  'Free'
  'Standard'
])
param sku string = 'Free'

resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
    tier: sku
  }
  properties: {}
}

output name string = staticWebApp.name
output url string = 'https://${staticWebApp.properties.defaultHostname}'
output id string = staticWebApp.id
