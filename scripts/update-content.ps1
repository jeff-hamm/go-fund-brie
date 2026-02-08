<# 
.SYNOPSIS
    Generates index.html from index.template.html using content from content.md
    
.DESCRIPTION
    Reads content.md, splits by --- separators, and replaces placeholders in
    the template to generate the final HTML file.
    
    Section mapping (top-to-bottom, left-to-right):
    - Section 0: Header title + Gold box (TL;DR)
    - Section 1: More surgery info (unused in current layout)
    - Section 2: Dark Teal box (Halp! section)
    - Section 3: Orange box (GoFundBrie)
    - Section 4: Teal box (Zelda facts)

.EXAMPLE
    .\update-content.ps1
    
.EXAMPLE
    .\update-content.ps1 -ContentFile "content.md" -TemplateFile "index.template.html" -OutputFile "index.html"
#>

param(
    [string]$ContentFile = "content.md",
    [string]$TemplateFile = "index.template.html",
    [string]$OutputFile = "index.html"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$contentPath = Join-Path $scriptDir $ContentFile
$templatePath = Join-Path $scriptDir $TemplateFile
$outputPath = Join-Path $scriptDir $OutputFile

# Verify files exist
if (-not (Test-Path $contentPath)) {
    Write-Error "Content file not found: $contentPath"
    exit 1
}
if (-not (Test-Path $templatePath)) {
    Write-Error "Template file not found: $templatePath"
    exit 1
}

# Read content.md and split by --- separators
$content = Get-Content $contentPath -Raw -Encoding UTF8
$sections = $content -split '\r?\n---\r?\n' | ForEach-Object { $_.Trim() } | Where-Object { $_ }

Write-Host "Parsing $ContentFile..." -ForegroundColor Cyan
Write-Host "  Found $($sections.Count) sections" -ForegroundColor Gray

# Parse a section to extract title (lines before ===) and content lines (after ===)
function Parse-Section {
    param([string]$Text)
    
    $lines = $Text -split '\r?\n'
    $titleLines = @()
    $contentLines = @()
    $foundSeparator = $false
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        
        # Check if this line is === (title separator)
        if ($line -match '^=+$') {
            $foundSeparator = $true
            continue
        }
        
        if (-not $foundSeparator) {
            # Before === - this is part of the title
            if ($line.Trim()) {
                $titleLines += $line.Trim()
            }
        } else {
            # After === - this is content
            if ($line.Trim()) {
                $contentLines += $line.Trim()
            }
        }
    }
    
    # If no === found, first line is title, rest is content
    if (-not $foundSeparator -and $titleLines.Count -gt 0) {
        $contentLines = $titleLines[1..($titleLines.Count - 1)]
        $titleLines = @($titleLines[0])
    }
    
    return @{
        Title = $titleLines -join "<br>"
        Lines = $contentLines
    }
}

# HTML escape function
function Escape-Html {
    param([string]$Text)
    return $Text -replace '&', '&amp;' -replace '<', '&lt;' -replace '>', '&gt;'
}

# Format a paragraph with given class
function Format-Paragraph {
    param(
        [string]$Text,
        [string]$Class = "box-text",
        [int]$Indent = 16
    )
    $spaces = " " * $Indent
    $escaped = Escape-Html $Text
    return "$spaces<p class=`"$Class`">$escaped</p>"
}

# Parse all sections
$parsed = @()
foreach ($section in $sections) {
    $parsed += Parse-Section -Text $section
}

Write-Host "  Section 0: $($parsed[0].Title -replace '<br>', ' / ')" -ForegroundColor Gray
Write-Host "  Section 1: $($parsed[1].Title)" -ForegroundColor Gray
Write-Host "  Section 2: $($parsed[2].Title)" -ForegroundColor Gray
Write-Host "  Section 3: $($parsed[3].Title)" -ForegroundColor Gray
Write-Host "  Section 4: $($parsed[4].Title)" -ForegroundColor Gray

# === Build content for each placeholder ===
# 5 sections → 5 boxes: Header, Gold, Dark Teal, Orange, Teal

# HEADER BANNER: Section 0
$headerTitle = $parsed[0].Title  # Already has <br> for line breaks
$headerLines = @()
foreach ($line in $parsed[0].Lines) {
    if ($line -match '^TL;DR') {
        $headerLines += "                <p class=`"header-text-line header-bold`">$(Escape-Html $line)</p>"
    } else {
        $headerLines += "                <p class=`"header-text-line`">$(Escape-Html $line)</p>"
    }
}
$headerContent = $headerLines -join "`n"

# GOLD BOX: Section 1
$goldTitle = Escape-Html $parsed[1].Title
$goldLines = @()
foreach ($line in $parsed[1].Lines) {
    $goldLines += Format-Paragraph -Text $line
}
$goldContent = $goldLines -join "`n"

# DARK TEAL BOX: Section 2
$darkTealTitle = $parsed[2].Title
$darkTealLines = @()
foreach ($line in $parsed[2].Lines) {
    $darkTealLines += Format-Paragraph -Text $line -Class "box-text box-text-small"
}
$darkTealContent = $darkTealLines -join "`n"

# ORANGE BOX: Section 3
$orangeTitle = Escape-Html $parsed[3].Title
$orangeLines = @()
# Main text (all lines except last, which is the cost)
$mainText = ($parsed[3].Lines[0..($parsed[3].Lines.Count - 2)] -join " ") + " 🤎"
$orangeLines += Format-Paragraph -Text $mainText
# Cost line (last line)
$costLine = $parsed[3].Lines[-1]
$orangeLines += Format-Paragraph -Text $costLine -Class "box-text box-text-bold"
$orangeContent = $orangeLines -join "`n"

# TEAL BOX: Section 4
$tealTitle = Escape-Html $parsed[4].Title
$tealLines = @()
# Process bullet points - combine continuation lines
$currentFact = ""
foreach ($line in $parsed[4].Lines) {
    if ($line -match '^-') {
        # New bullet point - save previous if exists
        if ($currentFact) {
            $tealLines += Format-Paragraph -Text $currentFact -Class "box-text box-text-small"
        }
        $currentFact = $line
    } else {
        # Continuation of previous bullet
        $currentFact += " " + $line
    }
}
# Don't forget last bullet
if ($currentFact) {
    $tealLines += Format-Paragraph -Text $currentFact -Class "box-text box-text-small"
}
$tealContent = $tealLines -join "`n"

# === Generate HTML from template ===
Write-Host "`nGenerating $OutputFile from template..." -ForegroundColor Cyan

$template = Get-Content $templatePath -Raw -Encoding UTF8

$html = $template `
    -replace '\{\{HEADER_TITLE\}\}', $headerTitle `
    -replace '\{\{HEADER_CONTENT\}\}', $headerContent `
    -replace '\{\{GOLD_TITLE\}\}', $goldTitle `
    -replace '\{\{GOLD_CONTENT\}\}', $goldContent `
    -replace '\{\{DARK_TEAL_TITLE\}\}', $darkTealTitle `
    -replace '\{\{DARK_TEAL_CONTENT\}\}', $darkTealContent `
    -replace '\{\{ORANGE_TITLE\}\}', $orangeTitle `
    -replace '\{\{ORANGE_CONTENT\}\}', $orangeContent `
    -replace '\{\{TEAL_TITLE\}\}', $tealTitle `
    -replace '\{\{TEAL_CONTENT\}\}', $tealContent

# Write output
$html | Set-Content $outputPath -Encoding UTF8 -NoNewline

Write-Host "Done! Generated $OutputFile" -ForegroundColor Green
Write-Host "`nContent mapping (5 sections -> 5 boxes):" -ForegroundColor Yellow
Write-Host "  Header:     Section 0 - $($parsed[0].Title -replace '<br>', ' / ')" -ForegroundColor Gray
Write-Host "  Gold:       Section 1 - $($parsed[1].Title)" -ForegroundColor Gray
Write-Host "  Dark Teal:  Section 2 - $($parsed[2].Title)" -ForegroundColor Gray
Write-Host "  Orange:     Section 3 - $($parsed[3].Title)" -ForegroundColor Gray
Write-Host "  Teal:       Section 4 - $($parsed[4].Title)" -ForegroundColor Gray
Write-Host "  Teal:       $($parsed[4].Title)" -ForegroundColor Gray
