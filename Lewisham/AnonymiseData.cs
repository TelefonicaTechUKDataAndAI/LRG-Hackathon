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
using System.Linq;
using System.Text;
using System.Security.Cryptography;

namespace Hackathon
{
    public static class AnonymiseData
    {
        [FunctionName("AnonymiseData")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("# HTTP trigger function to anonymise strings in Dataverse.");

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

                    // Anonymise columns
                    foreach (var entity in entities.Entities)
                    {
                        foreach (var columnName in columnNames)
                        {
                            var content = entity.GetAttributeValue<string>(columnName);

                            if (content != null)
                            {
                                // Anonymize the content
                                var anonymizedContent = AnonymizeContent(content);

                                // Update the entity with the anonymized content
                                entity[columnName] = anonymizedContent;
                                svc.Update(entity);

                                log.LogInformation($"Anonymized content for column {columnName}.");
                            }
                        }
                    }

                }
            }

            return new OkObjectResult($"Anonymisation process completed for table {tableName}.");
        }

        private static object AnonymizeContent(string rawData)
        {
            // Create a SHA256   
            using (SHA256 sha256Hash = SHA256.Create())
            {
                // ComputeHash - returns byte array  
                byte[] bytes = sha256Hash.ComputeHash(Encoding.UTF8.GetBytes(rawData));

                // Convert byte array to a string   
                StringBuilder builder = new StringBuilder();
                for (int i = 0; i < bytes.Length; i++)
                {
                    builder.Append(bytes[i].ToString("x2"));
                }
                return builder.ToString();
            }
        }
    }
}
