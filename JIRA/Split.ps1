# Splits a file into pieces of a given size.
#
# Usage:   .\Split.ps1 <file> <size> [outputDir]
# Example: .\Split.ps1 bigfile.log 10MB
#
# Output files are named <name>.part001<ext>, <name>.part002<ext>, ...
# To rejoin: copy /b name.part001.ext + name.part002.ext original.ext

param(
    [Parameter(Mandatory)] [string] $File,
    [Parameter(Mandatory)] [string] $Size,    # e.g. 500KB, 10MB, 1GB, or plain bytes
    [string] $OutputDir
)

$ErrorActionPreference = 'Stop'

function ConvertTo-Bytes([string] $text) {
    if ($text.Trim() -notmatch '^(\d+)\s*(KB|MB|GB)?$') {
        throw "Invalid size '$text'. Use a number with an optional KB, MB or GB suffix."
    }

    $bytes = [int64] $Matches[1]
    switch ($Matches[2]) {
        'KB' { $bytes *= 1KB }
        'MB' { $bytes *= 1MB }
        'GB' { $bytes *= 1GB }
    }

    if ($bytes -le 0) { throw 'Size must be greater than zero.' }
    return $bytes
}

$sourcePath = (Resolve-Path -LiteralPath $File).Path
$pieceSize  = ConvertTo-Bytes $Size

if (-not $OutputDir) { $OutputDir = Split-Path $sourcePath }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$baseName  = [IO.Path]::GetFileNameWithoutExtension($sourcePath)
$extension = [IO.Path]::GetExtension($sourcePath)

$buffer      = New-Object byte[] (1MB)
$pieceNumber = 0
$source      = [IO.File]::OpenRead($sourcePath)

try {
    while ($source.Position -lt $source.Length) {
        $pieceNumber++
        $pieceName = '{0}.part{1:D3}{2}' -f $baseName, $pieceNumber, $extension
        $piece     = [IO.File]::Create((Join-Path $OutputDir $pieceName))

        try {
            $bytesLeft = $pieceSize
            while ($bytesLeft -gt 0) {
                $toRead    = [Math]::Min($buffer.Length, $bytesLeft)
                $bytesRead = $source.Read($buffer, 0, $toRead)
                if ($bytesRead -eq 0) { break }    # end of source file

                $piece.Write($buffer, 0, $bytesRead)
                $bytesLeft -= $bytesRead
            }
        }
        finally {
            $piece.Dispose()
        }
    }
}
finally {
    $source.Dispose()
}

Write-Host "Created $pieceNumber part(s) in $OutputDir"
