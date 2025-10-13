# ISO 8583 Message Format Animation

An educational animation series created with [Manim Community Edition](https://www.manim.community/) that explains ISO 8583 message format used in card payment systems.

## Overview

This project creates a 4-6 minute animation explaining:
- **MTI (Message Type Indicator)**: Message classification
- **Bitmaps**: Indicating which data elements are present
- **Data Elements**: Fixed vs variable length fields
- **Network Transmission**: Socket transmission with length prefixes

## Installation

1. Ensure Python 3.12+ is installed (see `.python-version`)

2. Install dependencies:
   ```bash
   pip install manim
   ```

   Or if using uv:
   ```bash
   uv sync
   ```

## Usage

### Render Full Presentation (All Scenes Chained)
```bash
manim -pql main.py FullPresentation  # Low quality (fast, for testing)
manim -pqm main.py FullPresentation  # Medium quality
manim -pqh main.py FullPresentation  # High quality (production)
```

### Render Specific Scene
```bash
manim main.py ColdOpen              # Just the intro
manim main.py MeetTheMessage        # Message structure overview
manim main.py BitmapConcept         # Bitmap explanation
```

### Quality Options
```bash
-pql    # Low quality (480p, 15fps) - fast for testing
-pqm    # Medium quality (720p, 30fps)
-pqh    # High quality (1080p, 60fps) - production
```

The `-p` flag opens the video after rendering.

**Tip**: Start with `-pql` for quick iterations, then use `-pqh` for final export.

## Available Scenes

### Full Presentation
- **FullPresentation** - All scenes chained together (~4-6 minutes)

### Individual Scenes
1. **ColdOpen** - Title card (2-3s)
2. **WhatIsISO8583** - Introduction to the standard (10-15s)
3. **MeetTheMessage** - Full message structure display (15-20s)
4. **MTIDeepDive** - Message Type Indicator breakdown (20-30s)
5. **BitmapConcept** - How bitmaps work with bit numbering (25-35s)
6. **SecondaryBitmap** - Secondary bitmap explanation (8-12s)
7. **DataElementsFixedVsVariable** - Comparing field types (35-45s)
8. **AnotherFixedExample** - DE 7 timestamp breakdown (10-12s)
9. **DataTypesCheatSheet** - Quick reference for data types (10-15s)
10. **OnTheWire** - Network transmission visualization (20-30s)
11. **RecapAndPointers** - Final summary (10-15s)

## Output

Rendered videos are saved to:
```
media/videos/main/[quality]/[SceneName].mp4
```

## Key Features

- **Horizontal Message Layout**: All message segments are horizontally aligned
- **Clear Labeling**: Labels above hex bytes, descriptions below (no overlap)
- **Bit Numbering**: Binary displays show bit numbers 1-8 above the bits
- **Color-Coded**:
  - Cyan: MTI
  - Orange: Primary bitmap
  - Amber: Secondary bitmap
  - Green: Data elements
  - Purple: Length prefix

## Canonical Example

The animation uses a 60-byte ISO 8583 message:
- **MTI**: `0200` (financial request)
- **Primary Bitmap**: Sets bits 1, 2, 4, 7
- **Secondary Bitmap**: All zeros (present because bit 1 set)
- **DE 2**: PAN (LLVAR) - `16` + `4539681234567890`
- **DE 4**: Amount (N12) - `000000001000` ($10.00)
- **DE 7**: DateTime (N10) - `1013123039` (Oct 13, 12:30:39)

## Architecture

The project includes helper classes for reusable components:
- **ByteBlock**: Display hex bytes with labels
- **MessageStrip**: Horizontal message segment layout
- **BitmapVisualizer**: Binary display with bit numbering

## Reference

See `iso8583_manim_animation_script.md` for the complete animation script and technical details.

## License

Educational content for understanding ISO 8583 message format.
