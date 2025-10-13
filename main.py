"""
ISO 8583 Message Format Animation with Manim

Render commands:
  manim main.py                    # Render all scenes
  manim main.py MeetTheMessage     # Render specific scene
  manim -pqh main.py ColdOpen      # High quality render with preview
  manim -pql main.py               # Low quality for fast testing
"""

from manim import *
import numpy as np

# =============================================================================
# CONSTANTS
# =============================================================================

# Color scheme
COLOR_MTI = "#00CED1"  # Cyan
COLOR_PRIMARY_BITMAP = ORANGE
COLOR_SECONDARY_BITMAP = "#FFBF00"  # Amber
COLOR_DATA_ELEMENT = GREEN
COLOR_LENGTH_PREFIX = PURPLE

# =============================================================================
# CANONICAL MESSAGE DATA - BCD Encoding
# =============================================================================
# NOTE: ISO 8583 uses BCD (Binary Coded Decimal) encoding for numeric fields
# BCD packs 2 decimal digits per byte (e.g., 0200 → 02 00, not ASCII 30 32 30 30)

# MTI (BCD): 0200
MTI_HEX = "02 00"
MTI_ASCII = "0200"

# Primary bitmap (hex, 8 bytes): D0 20 00 00 00 00 00 00
# Bits set (1-based): 1, 2, 4, 11
PRIMARY_BITMAP_HEX = "D0 20 00 00 00 00 00 00"

# Secondary bitmap (hex, 8 bytes): all zeros (present because bit 1 = 1)
SECONDARY_BITMAP_HEX = "00 00 00 00 00 00 00 00"

# DE 2 (PAN, LLVAR): length (BCD) + value (BCD packed)
# Value: 4539681234567890 (16 digits)
DE2_HEX = "16 45 39 68 12 34 56 78 90"
DE2_LENGTH_HEX = "16"
DE2_LENGTH = "16"
DE2_VALUE_HEX = "45 39 68 12 34 56 78 90"
DE2_VALUE = "4539681234567890"

# DE 4 (Amount, N12 BCD): 000000001000 (for $10.00)
DE4_HEX = "00 00 00 00 10 00"
DE4_VALUE = "000000001000"

# DE 11 (STAN - System Trace Audit Number, N6 BCD): 123456
DE11_HEX = "12 34 56"
DE11_VALUE = "123456"

# Full message (no length prefix)
# MTI (2) + Primary (8) + Secondary (8) + DE2 (9) + DE4 (6) + DE11 (3) = 36 bytes
FULL_MESSAGE_HEX = "02 00 D0 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 45 39 68 12 34 56 78 90 00 00 00 00 10 00 12 34 56"

# Length prefix for sockets (2-byte big-endian): 00 24 (36 bytes)
LENGTH_PREFIX_HEX = "00 24"


# =============================================================================
# HELPER CLASSES
# =============================================================================

class ByteBlock(VGroup):
    """Displays a block of hex bytes with optional label."""

    def __init__(self, hex_string, label_text="", color=WHITE, label_position=UP, **kwargs):
        super().__init__(**kwargs)

        # Create hex text
        self.hex_text = Text(hex_string, font_size=24, font="monospace")
        self.hex_text.set_color(color)

        # Create label if provided
        if label_text:
            self.label = Text(label_text, font_size=20)
            self.label.next_to(self.hex_text, label_position, buff=0.2)
            self.add(self.hex_text, self.label)
        else:
            self.add(self.hex_text)


class MessageStrip(VGroup):
    """Horizontal layout of message segments with labels above and hex below."""

    def __init__(self, segments, **kwargs):
        """
        segments: list of dicts with keys: 'hex', 'label', 'color'
        """
        super().__init__(**kwargs)

        self.blocks = []
        for segment in segments:
            # Create label above (increased from 18 to 28)
            label = Text(segment['label'], font_size=28, weight=BOLD)
            label.set_color(segment['color'])

            # Create hex text below (increased from 20 to 30)
            hex_text = Text(segment['hex'], font_size=30, font="monospace")
            hex_text.set_color(segment['color'])

            # Stack them vertically
            block = VGroup(label, hex_text).arrange(DOWN, buff=0.2)
            self.blocks.append(block)

        # Arrange all blocks horizontally
        self.add(*self.blocks)
        self.arrange(RIGHT, buff=0.3)


class BitmapVisualizer(VGroup):
    """Displays binary representation of hex bytes with bit numbers."""

    def __init__(self, hex_value, num_bytes=1, **kwargs):
        super().__init__(**kwargs)

        # Convert hex to binary (8 or 16 bits)
        if num_bytes == 2:
            # Handle two bytes (e.g., "D0 20")
            hex_parts = hex_value.split()
            byte1 = int(hex_parts[0], 16)
            byte2 = int(hex_parts[1], 16)
            binary_string = format(byte1, '08b') + format(byte2, '08b')
            num_bits = 16
        else:
            # Handle single byte
            byte_value = int(hex_value, 16)
            binary_string = format(byte_value, '08b')
            num_bits = 8

        # Create bit numbers on top (aligned with digits)
        bit_numbers = VGroup()
        for i in range(1, num_bits + 1):
            num = Text(str(i), font_size=28, color=GRAY, weight=BOLD)
            bit_numbers.add(num)

        # Create binary digits
        binary_digits = VGroup()
        for bit in binary_string:
            digit = Text(bit, font_size=36, font="monospace", weight=BOLD)
            if bit == '1':
                digit.set_color(YELLOW)
            else:
                digit.set_color(GRAY)
            binary_digits.add(digit)

        # Arrange with same spacing
        bit_numbers.arrange(RIGHT, buff=0.35)
        binary_digits.arrange(RIGHT, buff=0.35)

        # Align bit numbers to binary digits
        for i, (num, digit) in enumerate(zip(bit_numbers, binary_digits)):
            num.align_to(digit, LEFT)

        # Stack them
        self.add(bit_numbers, binary_digits)
        self.arrange(DOWN, buff=0.35)

        self.bit_numbers = bit_numbers
        self.binary_digits = binary_digits
        self.binary_string = binary_string


# =============================================================================
# SCENE 0: COLD OPEN
# =============================================================================

class ColdOpen(Scene):
    """Cold open with title card (2-3s)."""

    def construct(self):
        # Title
        title = Text("ISO 8583 in 10 Minutes", font_size=60, weight=BOLD)
        title.set_color_by_gradient(COLOR_MTI, COLOR_DATA_ELEMENT)

        # Subtitle
        subtitle = Text("Messages behind card payments", font_size=30)
        subtitle.next_to(title, DOWN, buff=0.5)

        # Animate
        self.play(FadeIn(title, shift=DOWN), run_time=1)
        self.play(FadeIn(subtitle), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))


# =============================================================================
# SCENE 1: WHAT IS ISO 8583?
# =============================================================================

class WhatIsISO8583(Scene):
    """Introduction to ISO 8583 (10-15s)."""

    def construct(self):
        # Title
        title = Text("ISO 8583", font_size=50, weight=BOLD, color=COLOR_MTI)

        # Timeline
        timeline = Text("1987 → today", font_size=30)
        timeline.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(timeline), run_time=0.5)
        self.wait(0.5)

        # Move title up
        self.play(
            title.animate.scale(0.7).to_edge(UP),
            FadeOut(timeline)
        )

        # Bullet points
        bullets = VGroup(
            Text("• Defines how payment systems communicate", font_size=24),
            Text("• Authorization, financial transactions, reversals", font_size=24),
            Text("• Network management messages", font_size=24),
            Text("• Compact, efficient message layout", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        bullets.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(bullet, shift=RIGHT) for bullet in bullets], lag_ratio=0.3))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(bullets))


# =============================================================================
# SCENE 2: MEET THE MESSAGE
# =============================================================================

class MeetTheMessage(Scene):
    """Display the full message structure (15-20s)."""

    def construct(self):
        # Title
        title = Text("Meet the Message", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Create message segments - Row 1
        row1_segments = [
            {'hex': MTI_HEX, 'label': 'MTI', 'color': COLOR_MTI},
            {'hex': PRIMARY_BITMAP_HEX, 'label': 'Primary Bitmap', 'color': COLOR_PRIMARY_BITMAP},
            {'hex': SECONDARY_BITMAP_HEX, 'label': 'Secondary Bitmap', 'color': COLOR_SECONDARY_BITMAP},
        ]

        # Create message segments - Row 2
        row2_segments = [
            {'hex': DE2_HEX, 'label': 'DE 2 (PAN)', 'color': COLOR_DATA_ELEMENT},
        ]

        # Create message segments - Row 3
        row3_segments = [
            {'hex': DE4_HEX, 'label': 'DE 4 (Amount)', 'color': COLOR_DATA_ELEMENT},
            {'hex': DE11_HEX, 'label': 'DE 11 (STAN)', 'color': COLOR_DATA_ELEMENT},
        ]

        # Create rows
        row1 = MessageStrip(row1_segments)
        row1.scale(0.75)  # Increased from 0.6 to 0.75 for better visibility

        row2 = MessageStrip(row2_segments)
        row2.scale(0.75)  # Increased from 0.6 to 0.75 for better visibility

        row3 = MessageStrip(row3_segments)
        row3.scale(0.75)  # Increased from 0.6 to 0.75 for better visibility

        # Stack rows vertically
        message_display = VGroup(row1, row2, row3).arrange(DOWN, buff=0.5)
        message_display.next_to(title, DOWN, buff=0.5)

        # Animate all segments appearing
        all_blocks = row1.blocks + row2.blocks + row3.blocks
        self.play(LaggedStart(*[FadeIn(block, shift=UP) for block in all_blocks], lag_ratio=0.15))
        self.wait(1)

        # Add BCD encoding note
        bcd_note = Text("BCD encoding: 2 digits per byte", font_size=24, color=YELLOW, slant=ITALIC)
        bcd_note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(bcd_note))
        self.wait(1.5)
        self.play(FadeOut(bcd_note))

        # Highlight each segment with 3-second intervals
        highlights = []
        for block in all_blocks:
            highlight = SurroundingRectangle(block, color=YELLOW, buff=0.15, stroke_width=3)
            highlights.append(highlight)

        # Animate highlights sequentially
        for i, highlight in enumerate(highlights):
            if i == 0:
                self.play(Create(highlight), run_time=0.5)
            else:
                self.play(ReplacementTransform(highlights[i-1], highlight), run_time=0.5)
            self.wait(3)

        # Fade out the last highlight
        self.play(FadeOut(highlights[-1]))
        self.wait(1)

        # Store for potential next scene use
        self.message_display = message_display
        self.title = title


# =============================================================================
# SCENE 3: MTI DEEP DIVE
# =============================================================================

class MTIDeepDive(Scene):
    """Deep dive into MTI structure (20-30s)."""

    def construct(self):
        # Title
        title = Text("Message Type Indicator (MTI)", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # MTI bytes (BCD) with ASCII overlay
        mti_hex = Text(MTI_HEX, font_size=40, font="monospace", color=COLOR_MTI)
        mti_ascii = Text(MTI_ASCII, font_size=50, font="monospace", color=COLOR_MTI, weight=BOLD)

        # BCD explanation
        bcd_label = Text("BCD packed: 02 00", font_size=24, color=YELLOW)
        ascii_label = Text("Represents: 0200", font_size=24, color=YELLOW)

        mti_hex.move_to(UP * 1.5)
        mti_ascii.move_to(UP * 1.5)
        bcd_label.next_to(mti_hex, DOWN, buff=0.4)
        ascii_label.next_to(mti_ascii, DOWN, buff=0.4)

        self.play(FadeIn(mti_hex), FadeIn(bcd_label))
        self.wait(0.8)
        self.play(
            Transform(mti_hex, mti_ascii),
            Transform(bcd_label, ascii_label),
            run_time=1
        )
        self.wait(0.8)
        self.play(FadeOut(bcd_label))  # bcd_label now contains ascii_label after transform

        # MTI breakdown
        breakdown = VGroup(
            Text("0 — ISO version (legacy)", font_size=28),
            Text("2 — Class = Financial", font_size=28),
            Text("0 — Function = Request", font_size=28),
            Text("0 — Origin = Acquirer", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        breakdown.next_to(mti_hex, DOWN, buff=0.8)

        self.play(LaggedStart(*[Write(line) for line in breakdown], lag_ratio=0.3))
        self.wait(1)

        # Common MTI pairs
        self.play(FadeOut(breakdown))

        pairs = VGroup(
            Text("0100/0110 — Authorization request/response", font_size=30),
            Text("0200/0210 — Financial request/response", font_size=30, color=COLOR_MTI),
            Text("0800/0810 — Network management", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        pairs.next_to(mti_hex, DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(pair, shift=UP) for pair in pairs], lag_ratio=0.2))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(mti_hex), FadeOut(pairs))


# =============================================================================
# SCENE 4: BITMAP CONCEPT
# =============================================================================

class BitmapConcept(Scene):
    """Explain how bitmaps work (25-35s)."""

    def construct(self):
        # Title
        title = Text("The Bitmap", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Primary bitmap hex
        bitmap_hex = Text(PRIMARY_BITMAP_HEX, font_size=36, font="monospace", color=COLOR_PRIMARY_BITMAP)
        bitmap_hex.move_to(UP * 1.5)
        self.play(FadeIn(bitmap_hex))
        self.wait(0.5)

        # Focus on first two bytes D0 20 to show bit 11
        first_two_bytes = Text("D0 20", font_size=36, font="monospace", color=COLOR_PRIMARY_BITMAP)
        first_two_bytes.move_to(UP * 1.5)
        self.play(Transform(bitmap_hex, first_two_bytes), run_time=0.8)
        self.wait(0.5)

        # Expand to binary with bit numbers (2 bytes = 16 bits)
        binary_viz = BitmapVisualizer("D0 20", num_bytes=2)
        binary_viz.scale(0.7)  # Scale down to fit on screen
        binary_viz.move_to(ORIGIN + UP * 0.3)

        self.play(ReplacementTransform(bitmap_hex, binary_viz), run_time=1.5)
        self.wait(0.5)

        # Pulse the bits that are 1
        # D0 = 11010000: Bit 1 (index 0), Bit 2 (index 1), Bit 4 (index 3)
        # 20 = 00100000: Bit 11 (index 10)
        set_bits = [0, 1, 3, 10]
        pulses = [binary_viz.binary_digits[i].animate.scale(1.3).set_color(YELLOW) for i in set_bits]
        self.play(*pulses, run_time=0.5)
        self.play(*[binary_viz.binary_digits[i].animate.scale(1/1.3) for i in set_bits], run_time=0.5)

        # Show implications
        implications = VGroup(
            Text("Bit 1 = 1  →  Secondary bitmap present", font_size=26),
            Text("Bit 2 = 1  →  DE 2 present", font_size=26),
            Text("Bit 4 = 1  →  DE 4 present", font_size=26),
            Text("Bit 11 = 1  →  DE 11 present", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        implications.next_to(binary_viz, DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(imp, shift=RIGHT) for imp in implications], lag_ratio=0.3))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(binary_viz), FadeOut(implications))


# =============================================================================
# SCENE 5: SECONDARY BITMAP
# =============================================================================

class SecondaryBitmap(Scene):
    """Explain secondary bitmap (8-12s)."""

    def construct(self):
        # Title
        title = Text("Secondary Bitmap", font_size=40, weight=BOLD, color=COLOR_SECONDARY_BITMAP)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Secondary bitmap
        sec_bitmap = Text(SECONDARY_BITMAP_HEX, font_size=36, font="monospace", color=COLOR_SECONDARY_BITMAP)
        sec_bitmap.move_to(ORIGIN + UP * 0.5)
        self.play(FadeIn(sec_bitmap))
        self.wait(0.5)

        # Explanation
        explanation = VGroup(
            Text("Present because bit 1 is set in primary bitmap", font_size=24),
            Text("Extends field range to DE 65-128", font_size=24),
            Text("All zeros = no extended fields in this message", font_size=24),
        ).arrange(DOWN, buff=0.3)
        explanation.next_to(sec_bitmap, DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(exp, shift=UP) for exp in explanation], lag_ratio=0.3))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(sec_bitmap), FadeOut(explanation))


# =============================================================================
# SCENE 6: DATA ELEMENTS - FIXED VS VARIABLE
# =============================================================================

class DataElementsFixedVsVariable(Scene):
    """Compare fixed and variable length fields (35-45s)."""

    def construct(self):
        # Title
        title = Text("Data Elements: Fixed vs Variable", font_size=38, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # === DE 2 (LLVAR) - Upper section ===
        de2_label = Text("DE 2 — PAN (LLVAR, BCD)", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de2_label.move_to(UP * 2.2)

        de2_hex = Text(DE2_HEX, font_size=24, font="monospace", color=COLOR_DATA_ELEMENT)
        de2_hex.next_to(de2_label, DOWN, buff=0.5)

        self.play(Write(de2_label))
        self.play(FadeIn(de2_hex))
        self.wait(0.5)

        # Highlight length prefix (now 1 byte BCD)
        # Create invisible copy of just the "16" part to get proper positioning
        length_part = Text(DE2_LENGTH_HEX, font_size=24, font="monospace", color=YELLOW)
        # Position it to align with the start of de2_hex
        length_part.next_to(de2_label, DOWN, buff=0.5)
        length_part.align_to(de2_hex, LEFT)

        length_brace = Brace(length_part, DOWN, color=YELLOW)
        length_text = Text("length = 16 (1 byte)", font_size=24, color=YELLOW)
        length_text.next_to(length_brace, DOWN, buff=0.3)

        self.play(Create(length_brace), Write(length_text))
        self.wait(0.8)

        # Show value explanation - centered
        value_text = Text(f"Value: {DE2_VALUE} (BCD packed, 8 bytes)", font_size=24, color=COLOR_DATA_ELEMENT)
        value_text.next_to(length_text, DOWN, buff=0.4)
        # Center horizontally only (keep the vertical position from next_to)
        value_text.set_x(0)
        self.play(FadeIn(value_text))

        # Highlight the value momentarily
        self.play(Indicate(value_text, color=YELLOW, scale_factor=1.1))
        self.wait(0.8)

        # Fade out length annotation
        self.play(FadeOut(length_brace), FadeOut(length_text))
        self.wait(0.3)

        # === DE 4 (Fixed 12) - Lower section ===
        de4_label = Text("DE 4 — Amount (N 12, BCD)", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de4_label.move_to(DOWN * 1.2)

        de4_hex = Text(DE4_HEX, font_size=24, font="monospace", color=COLOR_DATA_ELEMENT)
        de4_hex.next_to(de4_label, DOWN, buff=0.5)

        self.play(Write(de4_label))
        self.play(FadeIn(de4_hex))
        self.wait(0.5)

        # Brace for entire field - now below
        de4_brace = Brace(de4_hex, DOWN, color=YELLOW)
        de4_brace_text = Text("12 digits (6 bytes BCD)", font_size=24, color=YELLOW)
        de4_brace_text.next_to(de4_brace, DOWN, buff=0.15)

        self.play(Create(de4_brace), Write(de4_brace_text))
        self.wait(0.5)

        # Show interpretation - to the right side
        amount_text = Text(f"= {DE4_VALUE} = $10.00", font_size=26, color=COLOR_DATA_ELEMENT)
        amount_text.next_to(de4_hex, RIGHT, buff=0.8)
        self.play(FadeIn(amount_text))

        # Highlight the amount momentarily
        self.play(Indicate(amount_text, color=YELLOW, scale_factor=1.1))
        self.wait(1.5)

        # Fade out annotations
        self.play(FadeOut(de4_brace), FadeOut(de4_brace_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])


# =============================================================================
# SCENE 7: ANOTHER FIXED EXAMPLE
# =============================================================================

class AnotherFixedExample(Scene):
    """Show DE 11 STAN (10-12s)."""

    def construct(self):
        # Title
        title = Text("DE 11 — STAN (System Trace Audit Number)", font_size=38, weight=BOLD, color=COLOR_DATA_ELEMENT)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # DE 11 hex (BCD)
        de11_hex = Text(DE11_HEX, font_size=40, font="monospace", color=COLOR_DATA_ELEMENT)
        de11_hex.move_to(UP * 1)

        bcd_note = Text("BCD: 12 34 56", font_size=28, color=YELLOW)
        bcd_note.next_to(de11_hex, DOWN, buff=0.4)

        self.play(FadeIn(de11_hex), FadeIn(bcd_note))
        self.wait(0.5)

        # Show decoded value
        de11_ascii = Text(DE11_VALUE, font_size=48, font="monospace", color=COLOR_DATA_ELEMENT, weight=BOLD)
        de11_ascii.move_to(UP * 1)

        decoded_note = Text("Represents: 123456", font_size=28, color=YELLOW)
        decoded_note.next_to(de11_ascii, DOWN, buff=0.4)

        self.play(
            Transform(de11_hex, de11_ascii),
            Transform(bcd_note, decoded_note),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(FadeOut(bcd_note))  # bcd_note now contains decoded_note after transform

        # Format explanation
        format_text = Text("Format: N 6 (6-digit numeric, 3 bytes BCD)", font_size=30)
        format_text.next_to(de11_hex, DOWN, buff=0.6)
        self.play(Write(format_text))
        self.wait(0.5)

        # Breakdown
        breakdown = Text("Unique transaction identifier for tracking", font_size=32, color=YELLOW)
        breakdown.next_to(format_text, DOWN, buff=0.5)
        self.play(FadeIn(breakdown, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(de11_hex), FadeOut(format_text), FadeOut(breakdown))


# =============================================================================
# SCENE 8: DATA TYPES CHEAT SHEET
# =============================================================================

class DataTypesCheatSheet(Scene):
    """Quick reference for data types (10-15s)."""

    def construct(self):
        # Title
        title = Text("Data Types Cheat Sheet", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Create grid of data types
        types = VGroup(
            Text("N — Numeric (0-9)", font_size=24),
            Text("AN — Alphanumeric (A-Z, 0-9)", font_size=24),
            Text("ANS — Printable (includes symbols)", font_size=24),
            Text("B — Binary data", font_size=24),
            Text("Z — Track data", font_size=24),
            Text("LLVAR — Variable, 2-digit length", font_size=24, color=YELLOW),
            Text("LLLVAR — Variable, 3-digit length", font_size=24, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        types.move_to(ORIGIN + UP * 0.5)

        # Add BCD encoding note
        bcd_note = Text("Encoding: BCD packs 2 decimal digits per byte",
                       font_size=26, color=ORANGE, weight=BOLD)
        bcd_note.to_edge(DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT) for t in types], lag_ratio=0.2))
        self.wait(1.5)
        self.play(FadeIn(bcd_note, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(types), FadeOut(bcd_note))


# =============================================================================
# SCENE 9: ON THE WIRE - LENGTH PREFIX & SOCKETS
# =============================================================================

class OnTheWire(Scene):
    """Show network transmission with length prefix (20-30s)."""

    def construct(self):
        # Title
        title = Text("On the Wire", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Original message (compact)
        message = Text("36-byte ISO 8583 message (BCD)", font_size=28, color=WHITE)
        message_box = SurroundingRectangle(message, color=WHITE, buff=0.2)
        message_group = VGroup(message, message_box)
        message_group.move_to(ORIGIN + UP * 1.5)

        self.play(Create(message_box), Write(message))
        self.wait(0.5)

        # Add length prefix
        prefix = Text(LENGTH_PREFIX_HEX, font_size=36, font="monospace", color=COLOR_LENGTH_PREFIX, weight=BOLD)
        prefix.next_to(message_group, LEFT, buff=0.4)

        prefix_label = Text("2-byte length", font_size=24, color=COLOR_LENGTH_PREFIX)
        prefix_label.next_to(prefix, UP, buff=0.3)

        decimal_label = Text("(36 decimal)", font_size=24, color=COLOR_LENGTH_PREFIX)
        decimal_label.next_to(prefix, DOWN, buff=0.3)

        self.play(FadeIn(prefix, shift=RIGHT), Write(prefix_label), Write(decimal_label))
        self.wait(1)

        # Clear screen for network diagram
        self.play(
            FadeOut(prefix_label),
            FadeOut(decimal_label),
        )

        # POS/Client and Host - positioned above the transmission line
        client = Text("POS/Client", font_size=26)
        client.move_to(LEFT * 5 + UP * 0.5)

        host = Text("Host", font_size=26)
        host.move_to(RIGHT * 5 + UP * 0.5)

        # Socket line - positioned below the labels
        socket_line = Line(LEFT * 4.5 + DOWN * 0.5, RIGHT * 4.5 + DOWN * 0.5, color=BLUE, stroke_width=3)

        self.play(Write(client), Write(host), Create(socket_line))
        self.wait(0.5)

        # Scale and position message with prefix at start of transmission line
        combined_frame = VGroup(prefix, message_box, message)
        self.play(combined_frame.animate.scale(0.5).move_to(socket_line.get_start() + UP * 0.3))
        self.wait(0.5)

        # Animate frame traveling across the line
        self.play(combined_frame.animate.move_to(socket_line.get_end() + UP * 0.3), run_time=2.5, rate_func=linear)
        self.wait(1)

        self.play(*[FadeOut(mob) for mob in self.mobjects])


# =============================================================================
# SCENE 10: RECAP & POINTERS
# =============================================================================

class RecapAndPointers(Scene):
    """Final recap (10-15s)."""

    def construct(self):
        # Title
        title = Text("Recap", font_size=48, weight=BOLD)
        title.set_color_by_gradient(COLOR_MTI, COLOR_DATA_ELEMENT)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Checklist
        checklist = VGroup(
            Text("✓ MTI classifies the message", font_size=28, color=COLOR_MTI),
            Text("✓ Bitmap lists present fields", font_size=28, color=COLOR_PRIMARY_BITMAP),
            Text("✓ Fixed vs variable elements", font_size=28, color=COLOR_DATA_ELEMENT),
            Text("✓ Length prefix for transport", font_size=28, color=COLOR_LENGTH_PREFIX),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        checklist.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(item, shift=UP) for item in checklist], lag_ratio=0.4))
        self.wait(2)

        # Final message
        final = Text("Questions ?", font_size=32)
        final.next_to(checklist, DOWN, buff=0.8)
        self.play(FadeIn(final, shift=UP))
        self.wait(2)

        self.play(FadeOut(title), FadeOut(checklist), FadeOut(final))


# =============================================================================
# OPTIONAL: Full Presentation (chains all scenes)
# =============================================================================

class FullPresentation(Scene):
    """Chains all scenes together into a single video."""

    def construct(self):
        # Scene 0: ColdOpen
        title = Text("ISO 8583 in 10 Minutes", font_size=60, weight=BOLD)
        title.set_color_by_gradient(COLOR_MTI, COLOR_DATA_ELEMENT)
        subtitle = Text("Messages behind card payments", font_size=30)
        subtitle.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(title, shift=DOWN), run_time=1)
        self.play(FadeIn(subtitle), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Scene 1: WhatIsISO8583
        title = Text("ISO 8583", font_size=50, weight=BOLD, color=COLOR_MTI)
        timeline = Text("1987 → today", font_size=30)
        timeline.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(timeline), run_time=0.5)
        self.wait(0.5)
        self.play(title.animate.scale(0.7).to_edge(UP), FadeOut(timeline))
        bullets = VGroup(
            Text("• Defines how payment systems communicate", font_size=24),
            Text("• Authorization, financial transactions, reversals", font_size=24),
            Text("• Network management messages", font_size=24),
            Text("• Compact, efficient message layout", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        bullets.next_to(title, DOWN, buff=0.8)
        self.play(LaggedStart(*[FadeIn(bullet, shift=RIGHT) for bullet in bullets], lag_ratio=0.3))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(bullets))

        # Scene 2: MeetTheMessage
        title = Text("Meet the Message", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)
        row1_segments = [
            {'hex': MTI_HEX, 'label': 'MTI', 'color': COLOR_MTI},
            {'hex': PRIMARY_BITMAP_HEX, 'label': 'Primary Bitmap', 'color': COLOR_PRIMARY_BITMAP},
            {'hex': SECONDARY_BITMAP_HEX, 'label': 'Secondary Bitmap', 'color': COLOR_SECONDARY_BITMAP},
        ]
        row2_segments = [
            {'hex': DE2_HEX, 'label': 'DE 2 (PAN)', 'color': COLOR_DATA_ELEMENT},
        ]
        row3_segments = [
            {'hex': DE4_HEX, 'label': 'DE 4 (Amount)', 'color': COLOR_DATA_ELEMENT},
            {'hex': DE11_HEX, 'label': 'DE 11 (STAN)', 'color': COLOR_DATA_ELEMENT},
        ]
        row1 = MessageStrip(row1_segments)
        row1.scale(0.75)
        row2 = MessageStrip(row2_segments)
        row2.scale(0.75)
        row3 = MessageStrip(row3_segments)
        row3.scale(0.75)
        message_display = VGroup(row1, row2, row3).arrange(DOWN, buff=0.5)
        message_display.next_to(title, DOWN, buff=0.5)
        all_blocks = row1.blocks + row2.blocks + row3.blocks
        self.play(LaggedStart(*[FadeIn(block, shift=UP) for block in all_blocks], lag_ratio=0.15))
        self.wait(1)

        # Add BCD encoding note
        bcd_note = Text("BCD encoding: 2 digits per byte", font_size=24, color=YELLOW, slant=ITALIC)
        bcd_note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(bcd_note))
        self.wait(1.5)
        self.play(FadeOut(bcd_note))

        # Highlight each segment with 3-second intervals
        highlights = []
        for block in all_blocks:
            highlight = SurroundingRectangle(block, color=YELLOW, buff=0.15, stroke_width=3)
            highlights.append(highlight)
        for i, highlight in enumerate(highlights):
            if i == 0:
                self.play(Create(highlight), run_time=0.5)
            else:
                self.play(ReplacementTransform(highlights[i-1], highlight), run_time=0.5)
            self.wait(3)
        self.play(FadeOut(highlights[-1]))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(message_display))

        # Scene 3: MTIDeepDive
        title = Text("Message Type Indicator (MTI)", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # MTI bytes (BCD) with ASCII overlay
        mti_hex = Text(MTI_HEX, font_size=40, font="monospace", color=COLOR_MTI)
        mti_ascii = Text(MTI_ASCII, font_size=50, font="monospace", color=COLOR_MTI, weight=BOLD)

        # BCD explanation
        bcd_label = Text("BCD packed: 02 00", font_size=24, color=YELLOW)
        ascii_label = Text("Represents: 0200", font_size=24, color=YELLOW)

        mti_hex.move_to(UP * 1.5)
        mti_ascii.move_to(UP * 1.5)
        bcd_label.next_to(mti_hex, DOWN, buff=0.4)
        ascii_label.next_to(mti_ascii, DOWN, buff=0.4)

        self.play(FadeIn(mti_hex), FadeIn(bcd_label))
        self.wait(0.8)
        self.play(
            Transform(mti_hex, mti_ascii),
            Transform(bcd_label, ascii_label),
            run_time=1
        )
        self.wait(0.8)
        self.play(FadeOut(bcd_label))  # bcd_label now contains ascii_label after transform

        # MTI breakdown
        breakdown = VGroup(
            Text("0 — ISO version (legacy)", font_size=28),
            Text("2 — Class = Financial", font_size=28),
            Text("0 — Function = Request", font_size=28),
            Text("0 — Origin = Acquirer", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        breakdown.next_to(mti_hex, DOWN, buff=0.8)
        self.play(LaggedStart(*[Write(line) for line in breakdown], lag_ratio=0.3))
        self.wait(1)
        self.play(FadeOut(breakdown))
        pairs = VGroup(
            Text("0100/0110 — Authorization request/response", font_size=30),
            Text("0200/0210 — Financial request/response", font_size=30, color=COLOR_MTI),
            Text("0800/0810 — Network management", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        pairs.next_to(mti_hex, DOWN, buff=0.8)
        self.play(LaggedStart(*[FadeIn(pair, shift=UP) for pair in pairs], lag_ratio=0.2))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(mti_hex), FadeOut(pairs))

        # Scene 4: BitmapConcept
        title = Text("The Bitmap", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)
        bitmap_hex = Text(PRIMARY_BITMAP_HEX, font_size=36, font="monospace", color=COLOR_PRIMARY_BITMAP)
        bitmap_hex.move_to(UP * 1.5)
        self.play(FadeIn(bitmap_hex))
        self.wait(0.5)
        first_two_bytes = Text("D0 20", font_size=36, font="monospace", color=COLOR_PRIMARY_BITMAP)
        first_two_bytes.move_to(UP * 1.5)
        self.play(Transform(bitmap_hex, first_two_bytes), run_time=0.8)
        self.wait(0.5)
        binary_viz = BitmapVisualizer("D0 20", num_bytes=2)
        binary_viz.scale(0.7)
        binary_viz.move_to(ORIGIN + UP * 0.3)
        self.play(ReplacementTransform(bitmap_hex, binary_viz), run_time=1.5)
        self.wait(0.5)
        set_bits = [0, 1, 3, 10]
        pulses = [binary_viz.binary_digits[i].animate.scale(1.3).set_color(YELLOW) for i in set_bits]
        self.play(*pulses, run_time=0.5)
        self.play(*[binary_viz.binary_digits[i].animate.scale(1/1.3) for i in set_bits], run_time=0.5)
        implications = VGroup(
            Text("Bit 1 = 1  →  Secondary bitmap present", font_size=26),
            Text("Bit 2 = 1  →  DE 2 present", font_size=26),
            Text("Bit 4 = 1  →  DE 4 present", font_size=26),
            Text("Bit 11 = 1  →  DE 11 present", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        implications.next_to(binary_viz, DOWN, buff=0.8)
        self.play(LaggedStart(*[FadeIn(imp, shift=RIGHT) for imp in implications], lag_ratio=0.3))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(binary_viz), FadeOut(implications))

        # Scene 5: SecondaryBitmap
        title = Text("Secondary Bitmap", font_size=40, weight=BOLD, color=COLOR_SECONDARY_BITMAP)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)
        sec_bitmap = Text(SECONDARY_BITMAP_HEX, font_size=36, font="monospace", color=COLOR_SECONDARY_BITMAP)
        sec_bitmap.move_to(ORIGIN + UP * 0.5)
        self.play(FadeIn(sec_bitmap))
        self.wait(0.5)
        explanation = VGroup(
            Text("Present because bit 1 is set in primary bitmap", font_size=24),
            Text("Extends field range to DE 65-128", font_size=24),
            Text("All zeros = no extended fields in this message", font_size=24),
        ).arrange(DOWN, buff=0.3)
        explanation.next_to(sec_bitmap, DOWN, buff=0.8)
        self.play(LaggedStart(*[FadeIn(exp, shift=UP) for exp in explanation], lag_ratio=0.3))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(sec_bitmap), FadeOut(explanation))

        # Scene 6: DataElementsFixedVsVariable
        title = Text("Data Elements: Fixed vs Variable", font_size=38, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # DE 2 (LLVAR) - Upper section
        de2_label = Text("DE 2 — PAN (LLVAR, BCD)", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de2_label.move_to(UP * 2.2)
        de2_hex = Text(DE2_HEX, font_size=24, font="monospace", color=COLOR_DATA_ELEMENT)
        de2_hex.next_to(de2_label, DOWN, buff=0.5)
        self.play(Write(de2_label))
        self.play(FadeIn(de2_hex))
        self.wait(0.5)

        # Highlight length prefix (1 byte BCD)
        length_part = Text(DE2_LENGTH_HEX, font_size=24, font="monospace", color=YELLOW)
        length_part.next_to(de2_label, DOWN, buff=0.5)
        length_part.align_to(de2_hex, LEFT)
        length_brace = Brace(length_part, DOWN, color=YELLOW)
        length_text = Text("length = 16 (1 byte)", font_size=24, color=YELLOW)
        length_text.next_to(length_brace, DOWN, buff=0.3)
        self.play(Create(length_brace), Write(length_text))
        self.wait(0.8)

        value_text = Text(f"Value: {DE2_VALUE} (BCD packed, 8 bytes)", font_size=24, color=COLOR_DATA_ELEMENT)
        value_text.next_to(length_text, DOWN, buff=0.4)
        value_text.set_x(0)
        self.play(FadeIn(value_text))

        # Highlight the value momentarily
        self.play(Indicate(value_text, color=YELLOW, scale_factor=1.1))
        self.wait(0.8)

        self.play(FadeOut(length_brace), FadeOut(length_text))
        self.wait(0.3)

        # DE 4 (Fixed 12) - Lower section
        de4_label = Text("DE 4 — Amount (N 12, BCD)", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de4_label.move_to(DOWN * 1.2)
        de4_hex = Text(DE4_HEX, font_size=24, font="monospace", color=COLOR_DATA_ELEMENT)
        de4_hex.next_to(de4_label, DOWN, buff=0.5)
        self.play(Write(de4_label))
        self.play(FadeIn(de4_hex))
        self.wait(0.5)

        de4_brace = Brace(de4_hex, DOWN, color=YELLOW)
        de4_brace_text = Text("12 digits (6 bytes BCD)", font_size=24, color=YELLOW)
        de4_brace_text.next_to(de4_brace, DOWN, buff=0.15)
        self.play(Create(de4_brace), Write(de4_brace_text))
        self.wait(0.5)

        amount_text = Text(f"= {DE4_VALUE} = $10.00", font_size=26, color=COLOR_DATA_ELEMENT)
        amount_text.next_to(de4_hex, RIGHT, buff=0.8)
        self.play(FadeIn(amount_text))

        # Highlight the amount momentarily
        self.play(Indicate(amount_text, color=YELLOW, scale_factor=1.1))
        self.wait(1.5)

        self.play(FadeOut(de4_brace), FadeOut(de4_brace_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])

        # Scene 7: AnotherFixedExample
        title = Text("DE 11 — STAN (System Trace Audit Number)", font_size=38, weight=BOLD, color=COLOR_DATA_ELEMENT)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # DE 11 hex (BCD)
        de11_hex = Text(DE11_HEX, font_size=40, font="monospace", color=COLOR_DATA_ELEMENT)
        de11_hex.move_to(UP * 1)
        bcd_note = Text("BCD: 12 34 56", font_size=28, color=YELLOW)
        bcd_note.next_to(de11_hex, DOWN, buff=0.4)
        self.play(FadeIn(de11_hex), FadeIn(bcd_note))
        self.wait(0.5)

        # Show decoded value
        de11_ascii = Text(DE11_VALUE, font_size=48, font="monospace", color=COLOR_DATA_ELEMENT, weight=BOLD)
        de11_ascii.move_to(UP * 1)
        decoded_note = Text("Represents: 123456", font_size=28, color=YELLOW)
        decoded_note.next_to(de11_ascii, DOWN, buff=0.4)
        self.play(Transform(de11_hex, de11_ascii), Transform(bcd_note, decoded_note), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(bcd_note))

        format_text = Text("Format: N 6 (6-digit numeric, 3 bytes BCD)", font_size=30)
        format_text.next_to(de11_hex, DOWN, buff=0.6)
        self.play(Write(format_text))
        self.wait(0.5)

        breakdown = Text("Unique transaction identifier for tracking", font_size=32, color=YELLOW)
        breakdown.next_to(format_text, DOWN, buff=0.5)
        self.play(FadeIn(breakdown, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(de11_hex), FadeOut(format_text), FadeOut(breakdown))

        # Scene 8: DataTypesCheatSheet
        title = Text("Data Types Cheat Sheet", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)
        types = VGroup(
            Text("N — Numeric (0-9)", font_size=24),
            Text("AN — Alphanumeric (A-Z, 0-9)", font_size=24),
            Text("ANS — Printable (includes symbols)", font_size=24),
            Text("B — Binary data", font_size=24),
            Text("Z — Track data", font_size=24),
            Text("LLVAR — Variable, 2-digit length", font_size=24, color=YELLOW),
            Text("LLLVAR — Variable, 3-digit length", font_size=24, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        types.move_to(ORIGIN + UP * 0.5)

        # Add BCD encoding note
        bcd_note = Text("Encoding: BCD packs 2 decimal digits per byte",
                       font_size=26, color=ORANGE, weight=BOLD)
        bcd_note.to_edge(DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT) for t in types], lag_ratio=0.2))
        self.wait(1.5)
        self.play(FadeIn(bcd_note, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(types), FadeOut(bcd_note))

        # Scene 9: OnTheWire
        title = Text("On the Wire", font_size=40, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Original message (compact)
        message = Text("36-byte ISO 8583 message (BCD)", font_size=28, color=WHITE)
        message_box = SurroundingRectangle(message, color=WHITE, buff=0.2)
        message_group = VGroup(message, message_box)
        message_group.move_to(ORIGIN + UP * 1.5)
        self.play(Create(message_box), Write(message))
        self.wait(0.5)

        # Add length prefix
        prefix = Text(LENGTH_PREFIX_HEX, font_size=36, font="monospace", color=COLOR_LENGTH_PREFIX, weight=BOLD)
        prefix.next_to(message_group, LEFT, buff=0.4)
        prefix_label = Text("2-byte length", font_size=24, color=COLOR_LENGTH_PREFIX)
        prefix_label.next_to(prefix, UP, buff=0.3)
        decimal_label = Text("(36 decimal)", font_size=24, color=COLOR_LENGTH_PREFIX)
        decimal_label.next_to(prefix, DOWN, buff=0.3)
        self.play(FadeIn(prefix, shift=RIGHT), Write(prefix_label), Write(decimal_label))
        self.wait(1)

        # Clear screen for network diagram
        self.play(FadeOut(prefix_label), FadeOut(decimal_label))

        # POS/Client and Host - positioned above the transmission line
        client = Text("POS/Client", font_size=26)
        client.move_to(LEFT * 5 + UP * 0.5)
        host = Text("Host", font_size=26)
        host.move_to(RIGHT * 5 + UP * 0.5)

        # Socket line - positioned below the labels
        socket_line = Line(LEFT * 4.5 + DOWN * 0.5, RIGHT * 4.5 + DOWN * 0.5, color=BLUE, stroke_width=3)
        self.play(Write(client), Write(host), Create(socket_line))
        self.wait(0.5)

        # Scale and position message with prefix at start of transmission line
        combined_frame = VGroup(prefix, message_box, message)
        self.play(combined_frame.animate.scale(0.5).move_to(socket_line.get_start() + UP * 0.3))
        self.wait(0.5)

        # Animate frame traveling across the line
        self.play(combined_frame.animate.move_to(socket_line.get_end() + UP * 0.3), run_time=2.5, rate_func=linear)
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

        # Scene 10: RecapAndPointers
        title = Text("Recap", font_size=48, weight=BOLD)
        title.set_color_by_gradient(COLOR_MTI, COLOR_DATA_ELEMENT)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.8)
        checklist = VGroup(
            Text("✓ MTI classifies the message", font_size=28, color=COLOR_MTI),
            Text("✓ Bitmap lists present fields", font_size=28, color=COLOR_PRIMARY_BITMAP),
            Text("✓ Fixed vs variable elements", font_size=28, color=COLOR_DATA_ELEMENT),
            Text("✓ Length prefix for transport", font_size=28, color=COLOR_LENGTH_PREFIX),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        checklist.move_to(ORIGIN)
        self.play(LaggedStart(*[FadeIn(item, shift=UP) for item in checklist], lag_ratio=0.4))
        self.wait(2)
        final = Text("Questions ?", font_size=32)
        final.next_to(checklist, DOWN, buff=0.8)
        self.play(FadeIn(final, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(checklist), FadeOut(final))
