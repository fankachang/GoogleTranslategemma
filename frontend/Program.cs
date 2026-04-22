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

// 若 BackendUrl 指向 localhost/127.0.0.1，動態替換為瀏覽器實際存取的主機，
// 以支援區域網路內其他電腦直接開啟頁面。
{
    var hostUri = new Uri(builder.HostEnvironment.BaseAddress);
    if (!hostUri.Host.Equals("localhost", StringComparison.OrdinalIgnoreCase)
        && !hostUri.Host.Equals("127.0.0.1", StringComparison.OrdinalIgnoreCase))
    {
        backendUrl = backendUrl
            .Replace("localhost", hostUri.Host, StringComparison.OrdinalIgnoreCase)
            .Replace("127.0.0.1", hostUri.Host, StringComparison.OrdinalIgnoreCase);
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

// 從後端取得公開設定（如字數上限），失敗時靜默保留預設值
try
{
    using var initHttp = new HttpClient { BaseAddress = new Uri(backendUrl) };
    var backendConfig = await initHttp.GetFromJsonAsync<AppConfigResponse>("/api/config");
    if (backendConfig != null && backendConfig.MaxInputLength > 0)
        appConfig.MaxInputLength = backendConfig.MaxInputLength;
}
catch (Exception ex)
{
    Console.Error.WriteLine($"[AppConfig] /api/config 初始化失敗，使用預設字數上限 {appConfig.MaxInputLength}：{ex.Message}");
}

await builder.Build().RunAsync();

