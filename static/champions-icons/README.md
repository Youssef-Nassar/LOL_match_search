# Champion Icons Folder

This folder contains champion icon images from the Figma design.

## How to Export Icons from Figma

1. Open the Figma file: https://www.figma.com/design/NoXz7eKVfBf1zcL6DfzSOB/v25.08-League-of-Legends.-All-Champions-Tier-List.--Community-?node-id=2-345

2. Select the champion icons you want to export

3. Right-click and select "Export" or use the Export panel

4. Export settings:
   - Format: PNG
   - Size: 120x120px or higher (recommended)
   - Naming: Use the champion's internal name (e.g., `Aatrox.png`, `Ahri.png`)

## File Naming Convention

Champion icons should be named using the champion's internal ID (lowercase, no spaces):
- `Aatrox` → `aatrox.png`
- `Miss Fortune` → `missfortune.png`
- `K'Sante` → `ksante.png`
- `Dr. Mundo` → `drmundo.png`

## Supported Formats

- PNG (recommended)
- JPG
- WebP

## Fallback

If a champion icon is not found in this folder, the application will automatically fallback to Riot Games' Data Dragon CDN.

## Champion Name Mapping

The application normalizes champion names by:
- Converting to lowercase
- Removing spaces
- Removing apostrophes (')
- Removing periods (.)

Examples:
- "Miss Fortune" → `missfortune.png`
- "K'Sante" → `ksante.png`
- "Dr. Mundo" → `drmundo.png`
