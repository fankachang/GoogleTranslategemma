namespace TranslateGemma;

public class AppConfig
{
    public string AppTitle { get; set; } = "TranslateGemma";
    /// <summary>
    /// 左上角 Logo 圖片路徑（相對於 wwwroot，例如 /images/logo.png）。
    /// 空白或未設定則不顯示圖示。
    /// </summary>
    public string? AppLogoUrl { get; set; }
}
