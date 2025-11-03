# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Manim animation project for creating an educational video about ISO 8583 message format and jPOS toolkit used in card payment systems. The goal is to produce a comprehensive animation explaining:

**Part 1 - ISO 8583 (4-6 minutes):**
- MTI (Message Type Identifier)
- Bitmaps (primary and secondary)
- Data elements (fixed and variable length)
- Socket transmission with length prefixes

**Part 2 - jPOS (5-7 minutes):**
- ISOMsg and Composite pattern
- Packagers (field specs to bytes)
- Channels (wire protocol adapters)
- QMUX (request/response multiplexing)

## Key Commands

- **Run animation**: `python main.py` (when implemented with Manim)
- **Development environment**: Python 3.12+ (see `.python-version`)
- **Package manager**: Uses `pyproject.toml` for dependency management

## Architecture

The project consists of two main parts:

### Part 1: ISO 8583 Fundamentals

Based on `iso8583_manim_animation_script.md`:

1. **Canonical example message**: 60-byte ISO 8583 message with:
   - MTI: `0200` (financial request)
   - Primary bitmap: `D2 00 00 00 00 00 00 00` (bits 1, 2, 4, 7 set)
   - Secondary bitmap: all zeros (present because bit 1 is set)
   - DE 2: PAN (LLVAR with length prefix)
   - DE 4: Amount (fixed 12 digits)
   - DE 7: Transmission date/time (fixed 10 digits)

2. **Visual system**: Dark background with color-coded elements:
   - Cyan: MTI
   - Orange/amber: Primary/secondary bitmaps
   - Green: Data elements
   - Purple: Length prefix

3. **Scene breakdown**: 10 distinct scenes from cold open through network transmission visualization to recap

### Part 2: jPOS Toolkit

Based on `jpos_manim_extension_script.md`:

1. **jPOS Components**:
   - ISOMsg: Message structure using Composite pattern
   - Packagers: Convert field specs to bytes (GenericPackager, ISOBasePackager)
   - Channels: Wire protocol adapters (ASCIIChannel, SSLChannel, LoopbackChannel)
   - QMUX: Request/response multiplexing with key-based correlation

2. **Visual system**: Extends ISO 8583 color scheme with:
   - Red: jPOS branding
   - Blue: Channels
   - Violet: QMUX
   - Coral orange: XML configuration
   - Yellow: Composite pattern highlights

3. **Scene breakdown**: 9 jPOS scenes (J0-J8) covering ISOMsg API, packager configuration, composite subfields, encoding details, and multiplexing

## Important Details

- All byte representations use **ASCII digits** and **hex bytes** for readability (not BCD/EBCDIC)
- Message bytes are shown as hex with overlays for ASCII interpretation
- Animations should use focus rectangles, braces, and binary "flip" reveals
- The length prefix (`00 3C`) is added only in the network transmission scene (scene 9)
- Timing target: 3:15-3:45 core content, expandable to 5:00 with pauses

## Manim Techniques

### Aligning Annotations to the Right of Code Blocks

When displaying code (like XML) with annotations aligned to the right, use this pattern to avoid overlaps (see main.py lines 2110-2115):

```python
# Define buffer space between code and annotations
ANNOTATION_BUFFER = 1.5

# Get the rightmost x-coordinate of the code block
code_right_x = xml_lines.get_right()[0]
annotation_column_x = code_right_x + ANNOTATION_BUFFER

# Position each annotation relative to its corresponding code line
for ann, code_line in zip(annotations, xml_lines[1:7]):
    ann.set_x(annotation_column_x, direction=LEFT)  # Align left edge of annotation
    ann.match_y(code_line)  # Match vertical position to code line
```

**Key points:**
- Use `get_right()[0]` to get the x-coordinate of the rightmost edge of the code block
- Set annotations using `set_x()` with `direction=LEFT` to align their left edges
- Use `match_y()` to vertically align annotations with their corresponding code lines
- This approach is **relative positioning** - no overlap even if code width changes

## Tools
- you can use gh to access github
- you can use available context7 mpc server (for example jpos doc)
- jpos: https://github.com/jpos/jPOS