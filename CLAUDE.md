# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Manim animation project for creating an educational video about ISO 8583 message format used in card payment systems. The goal is to produce a 4-6 minute animation explaining MTI (Message Type Identifier), bitmaps, data elements, and socket transmission with length prefixes.

## Key Commands

- **Run animation**: `python main.py` (when implemented with Manim)
- **Development environment**: Python 3.12+ (see `.python-version`)
- **Package manager**: Uses `pyproject.toml` for dependency management

## Architecture

The project will visualize ISO 8583 message structure based on `iso8583_manim_animation_script.md`, which contains:

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

## Important Details

- All byte representations use **ASCII digits** and **hex bytes** for readability (not BCD/EBCDIC)
- Message bytes are shown as hex with overlays for ASCII interpretation
- Animations should use focus rectangles, braces, and binary "flip" reveals
- The length prefix (`00 3C`) is added only in the network transmission scene (scene 9)
- Timing target: 3:15-3:45 core content, expandable to 5:00 with pauses
