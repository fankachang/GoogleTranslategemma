using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using MudBlazor.Services;
using System.Net.Http.Json;
using TranslateGemma;
using TranslateGemma.Models;
using TranslateGemma.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// 從 appsettings.json 讀取設定
var appConfig = builder.Configuration.Get<AppConfig>() ?? new AppConfig();
if (string.IsNullOrWhiteSpace(appConfig.AppTitle)) appConfig.AppTitle = "TranslateGemma";
builder.Services.AddSingleton(appConfig);

// BackendUrl 可在 appsettings.json 中設定，或透過容器環境變數 BACKEND_URL 注入。
// 若值仍為佔位符（非容器環境的 dotnet run），則回退至 localhost:8000。
var backendUrl = builder.Configuration["BackendUrl"] ?? "http://localhost:8000";
if (string.IsNullOrWhiteSpace(backendUrl) || backendUrl.StartsWith("${"))
    backendUrl = "http://localhost:8000";

// 前端與後端通常部署在同一台主機；若 BackendUrl 的 host 與瀏覽器實際存取的前端 host 不符，
// 自動將 BackendUrl 的 host 換成前端 host，以支援「將整套服務複製到另一台機器」的場景。
// 範例：BackendUrl 設為 10.1.1.99:8000，但實際在 10.34.26.255 上開啟 → 自動改成 10.34.26.255:8000。
{
    var frontendHost = new Uri(builder.HostEnvironment.BaseAddress).Host;
    if (!frontendHost.Equals("localhost", StringComparison.OrdinalIgnoreCase)
        && !frontendHost.Equals("127.0.0.1", StringComparison.OrdinalIgnoreCase))
    {
        try
        {
            var backendUri = new Uri(backendUrl);
            if (!backendUri.Host.Equals(frontendHost, StringComparison.OrdinalIgnoreCase))
            {
                var ub = new UriBuilder(backendUrl) { Host = frontendHost };
                backendUrl = ub.Uri.ToString().TrimEnd('/');
            }
        }
        catch { }
    }
}

builder.Services.AddScoped(sp => new HttpClient
{
    BaseAddress = new Uri(backendUrl),
    Timeout = System.Threading.Timeout.InfiniteTimeSpan, // 由 CancellationToken 控制逾時，不依賴 HttpClient 預設 100 秒
});

// MudBlazor 服務
builder.Services.AddMudServices();

// 應用程式服務
builder.Services.AddScoped<ITranslationService, TranslationService>();
builder.Services.AddScoped<LanguageService>();

// 從後端取得公開設定（如字數上限、功能開關），失敗時靜默保留預設值
try
{
    using var initHttp = new HttpClient { BaseAddress = new Uri(backendUrl) };
    var backendConfig = await initHttp.GetFromJsonAsync<AppConfigResponse>("/api/config");
    if (backendConfig != null && backendConfig.MaxInputLength > 0)
        appConfig.MaxInputLength = backendConfig.MaxInputLength;
    if (backendConfig != null)
        appConfig.LanguageSelectorEnabled = backendConfig.Features.LanguageSelector;
}
catch (Exception ex)
{
    Console.Error.WriteLine($"[AppConfig] /api/config 初始化失敗，使用預設字數上限 {appConfig.MaxInputLength}：{ex.Message}");
}

await builder.Build().RunAsync();

