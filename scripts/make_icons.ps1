Add-Type -AssemblyName System.Drawing

$srcPath = "C:\Users\Rasika\.gemini\antigravity-ide\brain\0dde3cc3-f0d4-4922-9a1b-3520b8852bf9\assistiq_modern_logo_1790591917558.jpg"
$img = [System.Drawing.Image]::FromFile($srcPath)

# Ensure directories
New-Item -ItemType Directory -Force -Path "E:\AssistIQ\frontend\public" | Out-Null
New-Item -ItemType Directory -Force -Path "E:\AssistIQ\frontend\build" | Out-Null
New-Item -ItemType Directory -Force -Path "E:\AssistIQ\flutter_app\assets\images" | Out-Null

function Save-ResizedImage($sourceImg, $width, $height, $targetPath) {
    $bmp = New-Object System.Drawing.Bitmap $width, $height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.DrawImage($sourceImg, 0, 0, $width, $height)
    $g.Dispose()
    
    $parent = Split-Path -Parent $targetPath
    if (!(Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    $bmp.Save($targetPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
}

# 1. Web & Flutter Main Logos (512x512)
Save-ResizedImage $img 512 512 "E:\AssistIQ\frontend\public\icon.png"
Save-ResizedImage $img 512 512 "E:\AssistIQ\frontend\build\icon.png"
Save-ResizedImage $img 512 512 "E:\AssistIQ\flutter_app\assets\images\app_logo.png"

# 2. 64x64 & 192x192 Favicons & PWA Icons
Save-ResizedImage $img 64 64 "E:\AssistIQ\frontend\public\favicon.png"
Save-ResizedImage $img 192 192 "E:\AssistIQ\frontend\public\logo192.png"
Save-ResizedImage $img 512 512 "E:\AssistIQ\frontend\public\logo512.png"

# 3. Android Mipmap Icons
Save-ResizedImage $img 48 48 "E:\AssistIQ\flutter_app\android\app\src\main\res\mipmap-mdpi\ic_launcher.png"
Save-ResizedImage $img 72 72 "E:\AssistIQ\flutter_app\android\app\src\main\res\mipmap-hdpi\ic_launcher.png"
Save-ResizedImage $img 96 96 "E:\AssistIQ\flutter_app\android\app\src\main\res\mipmap-xhdpi\ic_launcher.png"
Save-ResizedImage $img 144 144 "E:\AssistIQ\flutter_app\android\app\src\main\res\mipmap-xxhdpi\ic_launcher.png"
Save-ResizedImage $img 192 192 "E:\AssistIQ\flutter_app\android\app\src\main\res\mipmap-xxxhdpi\ic_launcher.png"

# 4. 256x256 ICO for Windows Desktop & Browsers
$bmp256 = New-Object System.Drawing.Bitmap 256, 256
$g256 = [System.Drawing.Graphics]::FromImage($bmp256)
$g256.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g256.DrawImage($img, 0, 0, 256, 256)
$g256.Dispose()

$hIcon = $bmp256.GetHicon()
$icon = [System.Drawing.Icon]::FromHandle($hIcon)

$fs = New-Object System.IO.FileStream("E:\AssistIQ\frontend\build\icon.ico", [System.IO.FileMode]::Create)
$icon.Save($fs)
$fs.Close()

Copy-Item "E:\AssistIQ\frontend\build\icon.ico" "E:\AssistIQ\frontend\public\favicon.ico" -Force

$img.Dispose()
$bmp256.Dispose()

Write-Host "All modern logo assets and Android mipmaps generated successfully!"
