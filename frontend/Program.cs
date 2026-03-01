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

var backendUrl = builder.Configuration["BackendUrl"] ?? "http://localhost:8000";
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

