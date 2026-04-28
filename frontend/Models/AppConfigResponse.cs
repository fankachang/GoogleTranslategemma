using System.Text.Json.Serialization;

namespace TranslateGemma.Models;

/// <summary>
/// 對應後端 GET /api/config 回應的 DTO。
/// </summary>
public record AppConfigResponse
{
    [JsonPropertyName("max_input_length")]
    public int MaxInputLength { get; init; } = 512;

    [JsonPropertyName("features")]
    public FeaturesConfig Features { get; init; } = new();
}

/// <summary>
/// 對應後端 features 設定區塊的 DTO。
/// </summary>
public record FeaturesConfig
{
    [JsonPropertyName("language_selector")]
    public bool LanguageSelector { get; init; } = false;
}
