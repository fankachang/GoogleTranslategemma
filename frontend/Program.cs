using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using MudBlazor.Services;
using TranslateGemma.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// HttpClient 指向後端 API（開發時為 localhost:8000）
var backendUrl = builder.Configuration["BackendUrl"] ?? "http://localhost:8000";
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(backendUrl) });

// MudBlazor 服務
builder.Services.AddMudServices();

// 應用程式服務
builder.Services.AddScoped<ITranslationService, TranslationService>();
builder.Services.AddScoped<LanguageService>();

await builder.Build().RunAsync();

