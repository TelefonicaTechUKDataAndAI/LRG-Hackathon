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
using System.Net.Http;
using System.Collections.Generic;
using System.Data;

namespace Hackathon
{
    public static class ExtractWeatherData
    {
        private static readonly HttpClient httpClient = new HttpClient();

        [FunctionName("ExtractWeatherData")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("# HTTP trigger function to extract weather data from API.");

            string latitude = req.Query["latitude"];
            string longitude = req.Query["longitude"];
            string start_date = req.Query["start_date"];
            string end_date = req.Query["end_date"];
            string daily = req.Query["daily"];
            string wind_speed_unit = req.Query["wind_speed_unit"];

            if (string.IsNullOrEmpty(latitude) || string.IsNullOrEmpty(longitude) || string.IsNullOrEmpty(start_date) || string.IsNullOrEmpty(end_date))
            {
                return new BadRequestObjectResult("Please provide latitude, longitude, start date and end date query parameters.");
            }

            // Prepare the API request
            string apiUrl = $"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&daily={daily}&wind_speed_unit={wind_speed_unit}";

            try
            {
                // Call the API
                HttpResponseMessage response = await httpClient.GetAsync(apiUrl);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();

                DataTable table = ConvertJsonToDataTable(responseBody);

                return new OkObjectResult(table);
            }
            catch (HttpRequestException e)
            {
                // Handle potential errors gracefully
                return new BadRequestObjectResult($"Error calling the API: {e.Message}");
            }

        }

        public static DataTable ConvertJsonToDataTable(string json)
        {
            Root root = JsonConvert.DeserializeObject<Root>(json);

            DataTable table = new DataTable();
            table.Columns.Add("Date", typeof(string));
            table.Columns.Add("WeatherCode", typeof(string));
            table.Columns.Add("MaxTemp", typeof(double));
            table.Columns.Add("MinTemp", typeof(double));
            table.Columns.Add("MeanTemp", typeof(double));
            table.Columns.Add("Sunrise", typeof(string));
            table.Columns.Add("Sunset", typeof(string));
            table.Columns.Add("DaylightDuration", typeof(double));
            table.Columns.Add("SunshineDuration", typeof(double));
            table.Columns.Add("PrecipitationSum", typeof(double));
            table.Columns.Add("RainSum", typeof(double));
            table.Columns.Add("SnowfallSum", typeof(double));
            table.Columns.Add("PrecipitationHours", typeof(double));
            table.Columns.Add("ShortwaveRadiationSum", typeof(double));

            for (int i = 0; i < root.daily.time.Count; i++)
            {
                DataRow row = table.NewRow();
                row["Date"] = root.daily.time[i];
                row["WeatherCode"] = root.daily.weather_code[i];
                row["MaxTemp"] = root.daily.temperature_2m_max[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.temperature_2m_max[i]);
                row["MinTemp"] = root.daily.temperature_2m_min[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.temperature_2m_min[i]);
                row["MeanTemp"] = root.daily.temperature_2m_mean[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.temperature_2m_mean[i]);
                row["Sunrise"] = root.daily.sunrise[i];
                row["Sunset"] = root.daily.sunset[i];
                row["DaylightDuration"] = root.daily.daylight_duration[i];
                row["SunshineDuration"] = root.daily.sunshine_duration[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.sunshine_duration[i]);
                row["PrecipitationSum"] = root.daily.precipitation_sum[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.precipitation_sum[i]);
                row["RainSum"] = root.daily.rain_sum[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.rain_sum[i]);
                row["SnowfallSum"] = root.daily.snowfall_sum[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.snowfall_sum[i]);
                row["PrecipitationHours"] = root.daily.precipitation_hours[i];
                row["ShortwaveRadiationSum"] = root.daily.shortwave_radiation_sum[i] == null ? (object)DBNull.Value : Convert.ToDouble(root.daily.shortwave_radiation_sum[i]);
                table.Rows.Add(row);
            }

            return table;
        }

        public class DailyUnits
        {
            public string time { get; set; }
            public string weather_code { get; set; }
            public string temperature_2m_max { get; set; }
            public string temperature_2m_min { get; set; }
            public string temperature_2m_mean { get; set; }
            public string sunrise { get; set; }
            public string sunset { get; set; }
            public string daylight_duration { get; set; }
            public string sunshine_duration { get; set; }
            public string precipitation_sum { get; set; }
            public string rain_sum { get; set; }
            public string snowfall_sum { get; set; }
            public string precipitation_hours { get; set; }
            public string shortwave_radiation_sum { get; set; }
        }

        public class Daily
        {
            public List<string> time { get; set; }
            public List<object> weather_code { get; set; }
            public List<object> temperature_2m_max { get; set; }
            public List<object> temperature_2m_min { get; set; }
            public List<object> temperature_2m_mean { get; set; }
            public List<string> sunrise { get; set; }
            public List<string> sunset { get; set; }
            public List<double> daylight_duration { get; set; }
            public List<object> sunshine_duration { get; set; }
            public List<object> precipitation_sum { get; set; }
            public List<object> rain_sum { get; set; }
            public List<object> snowfall_sum { get; set; }
            public List<double> precipitation_hours { get; set; }
            public List<object> shortwave_radiation_sum { get; set; }
        }

        public class Root
        {
            public double latitude { get; set; }
            public double longitude { get; set; }
            public double generationtime_ms { get; set; }
            public int utc_offset_seconds { get; set; }
            public string timezone { get; set; }
            public string timezone_abbreviation { get; set; }
            public double elevation { get; set; }
            public DailyUnits daily_units { get; set; }
            public Daily daily { get; set; }
        }
    }
}
