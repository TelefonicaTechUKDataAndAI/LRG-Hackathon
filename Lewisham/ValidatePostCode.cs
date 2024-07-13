using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Microsoft.PowerPlatform.Dataverse.Client;
using Microsoft.Rest;
using Microsoft.Xrm.Sdk.Query;
using Microsoft.Xrm.Sdk;
using System.Text.RegularExpressions;
using Microsoft.Xrm.Sdk.Messages;
using Microsoft.Xrm.Sdk.Metadata;

namespace Hackathon
{
    public static class ValidatePostCode
    {
        [FunctionName("ValidatePostCode")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("# HTTP trigger function to validate and update postcodes in Dataverse.");

            // Retrieve table name from the query string
            string tableName = req.Query["TableName"];
            string columns = req.Query["ColumnName"];
            
            string[] columnNames = columns.Split(',');
            
            if (string.IsNullOrEmpty(tableName))
            {
                return new BadRequestObjectResult("Please pass a TableName on the query string.");
            }

            // Setup the connection to Dataverse using environment variables
            string secretId = Environment.GetEnvironmentVariable("SecretId");
            string appId = Environment.GetEnvironmentVariable("AppId");
            string instanceUri = Environment.GetEnvironmentVariable("InstanceUri");

            string connectionString = $@"AuthType=ClientSecret;
                                SkipDiscovery=true;url={instanceUri};
                                Secret={secretId};
                                ClientId={appId};
                                RequireNewInstance=true";

            // Create a ServiceClient instance
            using (ServiceClient svc = new ServiceClient(connectionString))
            {
                if(svc.IsReady)
                {
                    // Define the query for the 'Pest Information' table
                    QueryExpression query = new QueryExpression(tableName)
                    {
                        ColumnSet = new ColumnSet(columnNames), // Assuming 'cr660_postcode' is the column name
                    };

                    // Execute the query
                    var entities = svc.RetrieveMultiple(query);

                    // Regex pattern for UK postcodes
                    string pattern = @"^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))\s?[0-9][A-Za-z]{2})$";
                    Regex regex = new Regex(pattern);

                    // Validate postcodes and update if invalid
                    foreach (var entity in entities.Entities)
                    {
                        foreach (var columnName in columnNames)
                        {
                            var postcode = entity.GetAttributeValue<string>(columnName);

                            if (postcode != null && !regex.IsMatch(postcode))
                            {
                                log.LogWarning($"Invalid postcode: {postcode}. Updating record with empty postcode.");

                                // Create an entity object with an empty postcode to update the record
                                Entity updateEntity = new Entity(tableName, entity.Id)
                                {
                                    [columnName] = string.Empty // Update the postcode column to empty
                                };

                                // Update the record in Dataverse
                                svc.Update(updateEntity);
                            }
                        }
                    }

                    // Create the request to retrieve entity metadata
                    //RetrieveEntityRequest retrieveEntityRequest = new RetrieveEntityRequest
                    //{
                    //    EntityFilters = EntityFilters.Attributes, // Retrieve only the attributes (columns)
                    //    LogicalName = tableName
                    //};

                    //// Execute the request
                    //RetrieveEntityResponse retrieveEntityResponse = (RetrieveEntityResponse)svc.Execute(retrieveEntityRequest);

                    //// Iterate through the attributes to list all columns
                    //foreach (var attributeMetadata in retrieveEntityResponse.EntityMetadata.Attributes)
                    //{
                    //    Console.WriteLine($"Attribute Logical Name: {attributeMetadata.LogicalName}, Type: {attributeMetadata.AttributeType}");
                    //}
                }
            }

            return new OkObjectResult($"Postcode validation and update process completed for table {tableName}.");
        }
    }
}
