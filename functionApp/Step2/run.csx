public static void Run(Stream myBlob, string name, TraceWriter log)
{
    log.Info($"C# Blob trigger function Processed blob\n Name:{name} \n Size: {myBlob.Length} Bytes");
}
#r "Newtonsoft.Json"
#r "System.Xml"
 
using System.Diagnostics;
using System.Net;
using System.Net.Security;
using System.Xml;
using Newtonsoft.Json;
 
#
public static void Run(TimerInfo myTimer, TraceWriter log)
{
    log.Info($"C# Timer trigger function executed at: {DateTime.Now}");
    var gwMgmtIp = "40.117.191.241,40.117.191.101";
    var apiKey1 = "LUFRPT04OTU5MjZ5UjBTNWtGMWwyeGxnb0k0bVZsSHM9MmQ5SzNLeTdycTdMem1scU5uR2pKdFl5L3U3dVo4MWV0WWM5WmNwMXAxZz0=";
    var firewall_cmd = "<show><system><state><filter>sw.mprelay.s1.dp0.stats.session</filter></state></system></show>";
    var concatUrl = "https://" + gwMgmtIp + "/api/?type=op&cmd=" + firewall_cmd + "&key=" + apiKey;
    WebClient wc = new WebClient();
    ServicePointManager.ServerCertificateValidationCallback = new RemoteCertificateValidationCallback(
        delegate
                { return true; }
    );
    ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls12;
    var responseData = wc.DownloadString(concatUrl);
    
    var xmldoc = new XmlDocument();
    xmldoc.LoadXml(responseData);
    string nodeList = xmldoc.GetElementsByTagName("result")[0].InnerText.Replace('\'', '"').Replace("sw.mprelay.s1.dp0.stats.session: ", "").Replace("\n", "");
    var json = JsonConvert.DeserializeObject<dynamic>(nodeList);
   string activeSessions = json["session_active"];
    log.Info($"Active session: {activeSessions} ");
}