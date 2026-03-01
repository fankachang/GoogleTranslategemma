using System.Text.Json.Serialization;

namespace TranslateGemma.Models;

/// <summary>
/// 對應後端 GET /api/config 回應的 DTO。
/// </summary>
public record AppConfigResponse(
    [property: JsonPropertyName("max_input_length")] int MaxInputLength
);
