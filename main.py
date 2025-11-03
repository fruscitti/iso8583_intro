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

# jPOS-specific colors
COLOR_JPOS_BRAND = RED              # jPOS branding
COLOR_ISOMSG = GREEN                # ISOMsg (reuse data element color)
COLOR_PACKAGER = ORANGE             # Packagers (reuse primary bitmap color)
COLOR_CHANNEL = BLUE                # Channels
COLOR_QMUX = "#8B00FF"              # QMUX (violet/purple)
COLOR_COMPOSITE = YELLOW            # Composite pattern highlights
COLOR_XML = "#FF6B35"               # XML snippets (coral orange)

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
# SCENE LOGIC - Helper Class (Option 1 Refactoring)
# =============================================================================

class ISO8583Scenes:
    """
    Helper class containing all scene construction logic.
    Each static method takes a Scene instance and constructs that scene's content.
    This eliminates code duplication between individual scenes and FullPresentation.
    """

    @staticmethod
    def construct_cold_open(scene):
        """Cold open with title card (2-3s)."""
        # Title
        title = Text("ISO 8583 in 10 Minutes", font_size=60, weight=BOLD)
        title.set_color_by_gradient(COLOR_MTI, COLOR_DATA_ELEMENT)

        # Subtitle
        subtitle = Text("Messages behind card payments", font_size=30)
        subtitle.next_to(title, DOWN, buff=0.5)

        # Animate
        scene.play(FadeIn(title, shift=DOWN), run_time=1)
        scene.play(FadeIn(subtitle), run_time=0.5)
        scene.wait(1)
        scene.play(FadeOut(title), FadeOut(subtitle))

    @staticmethod
    def construct_what_is_iso8583(scene):
        """Introduction to ISO 8583 (10-15s)."""
        # Title
        title = Text("ISO 8583", font_size=50, weight=BOLD, color=COLOR_MTI)

        # Timeline
        timeline = Text("1987 → today", font_size=30)
        timeline.next_to(title, DOWN, buff=0.4)

        scene.play(Write(title), run_time=0.8)
        scene.play(FadeIn(timeline), run_time=0.5)
        scene.wait(0.5)

        # Move title up
        scene.play(
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

        scene.play(LaggedStart(*[FadeIn(bullet, shift=RIGHT) for bullet in bullets], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title), FadeOut(bullets))

    @staticmethod
    def construct_meet_the_message(scene):
        """Display the full message structure (15-20s)."""
        # Title
        title = Text("Meet the Message", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

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
        row1.scale(0.75)

        row2 = MessageStrip(row2_segments)
        row2.scale(0.75)

        row3 = MessageStrip(row3_segments)
        row3.scale(0.75)

        # Arrange rows vertically
        message_display = VGroup(row1, row2, row3).arrange(DOWN, buff=0.5)
        message_display.next_to(title, DOWN, buff=0.8)

        # Animate all segments appearing
        all_blocks = row1.blocks + row2.blocks + row3.blocks
        scene.play(LaggedStart(*[FadeIn(block, shift=UP) for block in all_blocks], lag_ratio=0.15))
        scene.wait(1)

        # Add BCD encoding note
        bcd_note = Text("BCD encoding: 2 digits per byte", font_size=24, color=YELLOW, slant=ITALIC)
        bcd_note.to_edge(DOWN, buff=0.5)
        scene.play(FadeIn(bcd_note))
        scene.wait(1.5)
        scene.play(FadeOut(bcd_note))

        # Highlight each segment with 3-second intervals
        highlights = []
        for block in all_blocks:
            highlight = SurroundingRectangle(block, color=YELLOW, buff=0.15, stroke_width=3)
            highlights.append(highlight)

        for i, highlight in enumerate(highlights):
            if i == 0:
                scene.play(Create(highlight), run_time=0.5)
            else:
                scene.play(ReplacementTransform(highlights[i-1], highlight), run_time=0.5)
            scene.wait(3)

        scene.play(FadeOut(highlights[-1]))
        scene.wait(1)
        scene.play(FadeOut(title), FadeOut(message_display))

    @staticmethod
    def construct_mti_deep_dive(scene):
        """MTI breakdown (20-30s)."""
        # Title
        title = Text("Message Type Indicator (MTI)", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

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

        scene.play(FadeIn(mti_hex), FadeIn(bcd_label))
        scene.wait(0.8)
        scene.play(
            Transform(mti_hex, mti_ascii),
            Transform(bcd_label, ascii_label),
            run_time=1
        )
        scene.wait(0.8)
        scene.play(FadeOut(bcd_label))  # bcd_label now contains ascii_label after transform

        # MTI breakdown
        breakdown = VGroup(
            Text("0 — ISO version (legacy)", font_size=28),
            Text("2 — Class = Financial", font_size=28),
            Text("0 — Function = Request", font_size=28),
            Text("0 — Origin = Acquirer", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        breakdown.next_to(mti_hex, DOWN, buff=0.8)

        scene.play(LaggedStart(*[FadeIn(line, shift=RIGHT) for line in breakdown], lag_ratio=0.3))
        scene.wait(1)
        scene.play(FadeOut(breakdown))

        # Common MTI pairs
        pairs = VGroup(
            Text("0100/0110 — Authorization request/response", font_size=30),
            Text("0200/0210 — Financial request/response", font_size=30, color=COLOR_MTI),
            Text("0800/0810 — Network management", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        pairs.next_to(mti_hex, DOWN, buff=0.8)

        scene.play(LaggedStart(*[FadeIn(pair, shift=RIGHT) for pair in pairs], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title), FadeOut(mti_hex), FadeOut(pairs))

    @staticmethod
    def construct_bitmap_concept(scene):
        """Bitmap explanation with bit numbering (25-35s)."""
        # Title
        title = Text("Bitmap Concept", font_size=40, weight=BOLD, color=COLOR_PRIMARY_BITMAP)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Show first two bytes of primary bitmap
        bitmap_hex = Text(PRIMARY_BITMAP_HEX, font_size=36, font="monospace", color=COLOR_PRIMARY_BITMAP)
        bitmap_hex.move_to(UP * 2)
        scene.play(FadeIn(bitmap_hex))
        scene.wait(0.5)

        # Highlight first two bytes
        first_two_bytes = Text("D0 20", font_size=36, font="monospace", color=COLOR_PRIMARY_BITMAP)
        first_two_bytes.move_to(UP * 2)
        scene.play(Transform(bitmap_hex, first_two_bytes))
        scene.wait(0.5)

        # Create binary visualization for 2 bytes (16 bits)
        binary_viz = BitmapVisualizer("D0 20", num_bytes=2)
        binary_viz.scale(0.7)
        binary_viz.move_to(ORIGIN + UP * 0.3)

        scene.play(FadeIn(binary_viz))
        scene.wait(0.5)

        # Pulse the set bits: D0 = 11010000 (bits 1,2,4), 20 = 00100000 (bit 11)
        # Bit indices: 0,1,3 for first byte, 10 for second byte
        set_bits = [0, 1, 3, 10]
        pulses = [binary_viz.binary_digits[i].animate.scale(1.3).set_color(YELLOW) for i in set_bits]
        scene.play(*pulses, run_time=0.5)
        scene.play(*[binary_viz.binary_digits[i].animate.scale(1/1.3) for i in set_bits], run_time=0.5)

        # Show implications
        implications = VGroup(
            Text("Bit 1 = 1  →  Secondary bitmap present", font_size=26),
            Text("Bit 2 = 1  →  DE 2 present", font_size=26),
            Text("Bit 4 = 1  →  DE 4 present", font_size=26),
            Text("Bit 11 = 1  →  DE 11 present", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        implications.next_to(binary_viz, DOWN, buff=0.8)

        scene.play(LaggedStart(*[FadeIn(imp, shift=RIGHT) for imp in implications], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title), FadeOut(bitmap_hex), FadeOut(binary_viz), FadeOut(implications))

    @staticmethod
    def construct_secondary_bitmap(scene):
        """Secondary bitmap explanation (8-12s)."""
        # Title
        title = Text("Secondary Bitmap", font_size=40, weight=BOLD, color=COLOR_SECONDARY_BITMAP)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Secondary bitmap
        sec_bitmap = Text(SECONDARY_BITMAP_HEX, font_size=36, font="monospace", color=COLOR_SECONDARY_BITMAP)
        sec_bitmap.move_to(ORIGIN + UP * 0.5)
        scene.play(FadeIn(sec_bitmap))
        scene.wait(0.5)

        # Explanation
        explanation = VGroup(
            Text("Present because bit 1 is set in primary bitmap", font_size=24),
            Text("Extends field range to DE 65-128", font_size=24),
            Text("All zeros = no extended fields in this message", font_size=24),
        ).arrange(DOWN, buff=0.3)
        explanation.next_to(sec_bitmap, DOWN, buff=0.8)

        scene.play(LaggedStart(*[FadeIn(exp, shift=UP) for exp in explanation], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title), FadeOut(sec_bitmap), FadeOut(explanation))

    @staticmethod
    def construct_data_elements_fixed_vs_variable(scene):
        """Compare fixed and variable length fields (35-45s)."""
        # Title
        title = Text("Data Elements: Fixed vs Variable", font_size=38, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # === DE 2 (LLVAR) - Upper section ===
        de2_label = Text("DE 2 — PAN (LLVAR, BCD)", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de2_label.move_to(UP * 2.2)

        de2_hex = Text(DE2_HEX, font_size=24, font="monospace", color=COLOR_DATA_ELEMENT)
        de2_hex.next_to(de2_label, DOWN, buff=0.5)

        scene.play(Write(de2_label))
        scene.play(FadeIn(de2_hex))
        scene.wait(0.5)

        # Highlight length prefix (now 1 byte BCD)
        length_part = Text(DE2_LENGTH_HEX, font_size=24, font="monospace", color=YELLOW)
        length_part.next_to(de2_label, DOWN, buff=0.5)
        length_part.align_to(de2_hex, LEFT)

        length_brace = Brace(length_part, DOWN, color=YELLOW)
        length_text = Text("length = 16 (1 byte)", font_size=24, color=YELLOW)
        length_text.next_to(length_brace, DOWN, buff=0.3)

        scene.play(Create(length_brace), Write(length_text))
        scene.wait(0.8)

        # Show value explanation - centered
        value_text = Text(f"Value: {DE2_VALUE} (BCD packed, 8 bytes)", font_size=24, color=COLOR_DATA_ELEMENT)
        value_text.next_to(length_text, DOWN, buff=0.4)
        value_text.set_x(0)
        scene.play(FadeIn(value_text))

        # Highlight the value momentarily
        scene.play(Indicate(value_text, color=YELLOW, scale_factor=1.1))
        scene.wait(0.8)

        # Fade out length annotation
        scene.play(FadeOut(length_brace), FadeOut(length_text))
        scene.wait(0.3)

        # === DE 4 (Fixed 12) - Lower section ===
        de4_label = Text("DE 4 — Amount (N 12, BCD)", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de4_label.move_to(DOWN * 1.2)

        de4_hex = Text(DE4_HEX, font_size=24, font="monospace", color=COLOR_DATA_ELEMENT)
        de4_hex.next_to(de4_label, DOWN, buff=0.5)

        scene.play(Write(de4_label))
        scene.play(FadeIn(de4_hex))
        scene.wait(0.5)

        # Brace for entire field - now below
        de4_brace = Brace(de4_hex, DOWN, color=YELLOW)
        de4_brace_text = Text("12 digits (6 bytes BCD)", font_size=24, color=YELLOW)
        de4_brace_text.next_to(de4_brace, DOWN, buff=0.15)

        scene.play(Create(de4_brace), Write(de4_brace_text))
        scene.wait(0.5)

        # Show interpretation - to the right side
        amount_text = Text(f"= {DE4_VALUE} = $10.00", font_size=26, color=COLOR_DATA_ELEMENT)
        amount_text.next_to(de4_hex, RIGHT, buff=0.8)
        scene.play(FadeIn(amount_text))

        # Highlight the amount momentarily
        scene.play(Indicate(amount_text, color=YELLOW, scale_factor=1.1))
        scene.wait(1.5)

        # Fade out annotations
        scene.play(FadeOut(de4_brace), FadeOut(de4_brace_text))

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

    @staticmethod
    def construct_another_fixed_example(scene):
        """Show DE 11 STAN (10-12s)."""
        # Title
        title = Text("DE 11 — STAN (System Trace Audit Number)", font_size=38, weight=BOLD, color=COLOR_DATA_ELEMENT)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # DE 11 hex (BCD)
        de11_hex = Text(DE11_HEX, font_size=40, font="monospace", color=COLOR_DATA_ELEMENT)
        de11_hex.move_to(UP * 1)

        bcd_note = Text("BCD: 12 34 56", font_size=28, color=YELLOW)
        bcd_note.next_to(de11_hex, DOWN, buff=0.4)

        scene.play(FadeIn(de11_hex), FadeIn(bcd_note))
        scene.wait(0.5)

        # Show decoded value
        de11_ascii = Text(DE11_VALUE, font_size=48, font="monospace", color=COLOR_DATA_ELEMENT, weight=BOLD)
        de11_ascii.move_to(UP * 1)

        decoded_note = Text("Represents: 123456", font_size=28, color=YELLOW)
        decoded_note.next_to(de11_ascii, DOWN, buff=0.4)

        scene.play(
            Transform(de11_hex, de11_ascii),
            Transform(bcd_note, decoded_note),
            run_time=0.8
        )
        scene.wait(0.5)
        scene.play(FadeOut(bcd_note))

        # Format explanation
        format_text = Text("Format: N 6 (6-digit numeric, 3 bytes BCD)", font_size=30)
        format_text.next_to(de11_hex, DOWN, buff=0.6)
        scene.play(Write(format_text))
        scene.wait(0.5)

        # Breakdown
        breakdown = Text("Unique transaction identifier for tracking", font_size=32, color=YELLOW)
        breakdown.next_to(format_text, DOWN, buff=0.5)
        scene.play(FadeIn(breakdown, shift=UP))
        scene.wait(2)

        scene.play(FadeOut(title), FadeOut(de11_hex), FadeOut(format_text), FadeOut(breakdown))

    @staticmethod
    def construct_data_types_cheat_sheet(scene):
        """Data types reference (10-15s)."""
        # Title
        title = Text("Data Types Cheat Sheet", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

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

        scene.play(LaggedStart(*[FadeIn(t, shift=RIGHT) for t in types], lag_ratio=0.2))
        scene.wait(1.5)
        scene.play(FadeIn(bcd_note, shift=UP))
        scene.wait(2)
        scene.play(FadeOut(title), FadeOut(types), FadeOut(bcd_note))

    @staticmethod
    def construct_on_the_wire(scene):
        """Network transmission visualization (20-30s)."""
        # Title
        title = Text("On the Wire", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Original message (compact)
        message = Text("36-byte ISO 8583 message (BCD)", font_size=28, color=WHITE)
        message_box = SurroundingRectangle(message, color=WHITE, buff=0.2)
        message_group = VGroup(message, message_box)
        message_group.move_to(ORIGIN + UP * 1.5)

        scene.play(Create(message_box), Write(message))
        scene.wait(0.5)

        # Add length prefix
        prefix = Text(LENGTH_PREFIX_HEX, font_size=36, font="monospace", color=COLOR_LENGTH_PREFIX, weight=BOLD)
        prefix.next_to(message_group, LEFT, buff=0.4)

        prefix_label = Text("2-byte length", font_size=24, color=COLOR_LENGTH_PREFIX)
        prefix_label.next_to(prefix, UP, buff=0.3)

        decimal_label = Text("(36 decimal)", font_size=24, color=COLOR_LENGTH_PREFIX)
        decimal_label.next_to(prefix, DOWN, buff=0.3)

        scene.play(FadeIn(prefix, shift=RIGHT), Write(prefix_label), Write(decimal_label))
        scene.wait(1)

        # Clear screen for network diagram
        scene.play(
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

        scene.play(Write(client), Write(host), Create(socket_line))
        scene.wait(0.5)

        # Scale and position message with prefix at start of transmission line
        combined_frame = VGroup(prefix, message_box, message)
        scene.play(combined_frame.animate.scale(0.5).move_to(socket_line.get_start() + UP * 0.3))
        scene.wait(0.5)

        # Animate frame traveling across the line
        scene.play(combined_frame.animate.move_to(socket_line.get_end() + UP * 0.3), run_time=2.5, rate_func=linear)
        scene.wait(1)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

    @staticmethod
    def construct_recap_and_pointers(scene):
        """Final summary (10-15s)."""
        # Title
        title = Text("Recap", font_size=48, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Checklist
        checklist = VGroup(
            Text("✓ MTI classifies the message", font_size=28, color=COLOR_MTI),
            Text("✓ Bitmap lists present fields", font_size=28, color=COLOR_PRIMARY_BITMAP),
            Text("✓ Fixed vs variable elements", font_size=28, color=COLOR_DATA_ELEMENT),
            Text("✓ Length prefix for transport", font_size=28, color=COLOR_LENGTH_PREFIX),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        checklist.move_to(ORIGIN)

        scene.play(LaggedStart(*[FadeIn(item, shift=UP) for item in checklist], lag_ratio=0.4))
        scene.wait(2)

        # Final message
        final = Text("Questions ?", font_size=32)
        final.next_to(checklist, DOWN, buff=0.8)
        scene.play(FadeIn(final, shift=UP))
        scene.wait(2)

        scene.play(FadeOut(title), FadeOut(checklist), FadeOut(final))


# =============================================================================
# jPOS SCENE LOGIC - Helper Class
# =============================================================================

class JPOSScenes:
    """
    Helper class containing all jPOS scene construction logic.
    Each static method takes a Scene instance and constructs that scene's content.
    """

    @staticmethod
    def construct_jpos_intro(scene):
        """Intro to jPOS (8-12s)."""
        # Title with jPOS branding
        title = Text("jPOS", font_size=60, weight=BOLD, color=COLOR_JPOS_BRAND)
        subtitle = Text("ISO 8583 toolkit for Java", font_size=32)
        subtitle.next_to(title, DOWN, buff=0.4)

        title_group = VGroup(title, subtitle)
        title_group.move_to(UP * 2)

        scene.play(Write(title), run_time=0.8)
        scene.play(FadeIn(subtitle), run_time=0.5)
        scene.wait(0.5)

        # Four key components as bubbles
        components = VGroup(
            Text("ISOMsg", font_size=28, color=COLOR_ISOMSG, weight=BOLD),
            Text("Packagers", font_size=28, color=COLOR_PACKAGER, weight=BOLD),
            Text("Channels", font_size=28, color=COLOR_CHANNEL, weight=BOLD),
            Text("QMUX", font_size=28, color=COLOR_QMUX, weight=BOLD),
        ).arrange_in_grid(rows=2, cols=2, buff=0.8)
        components.move_to(ORIGIN)

        # Add surrounding rectangles to create bubbles
        bubbles = VGroup()
        for comp in components:
            bubble = SurroundingRectangle(comp, color=comp.get_color(), buff=0.3, corner_radius=0.2)
            bubbles.add(VGroup(bubble, comp))

        scene.play(LaggedStart(*[FadeIn(bubble, shift=UP, scale=0.8) for bubble in bubbles], lag_ratio=0.2))
        scene.wait(0.8)

        # Bullets about features
        scene.play(FadeOut(bubbles))

        bullets = VGroup(
            Text("• Mature & modular ISO 8583 toolkit", font_size=24),
            Text("• Pluggable packagers & channels", font_size=24),
            Text("• Multiplexing (QMUX) for request/response", font_size=24),
            Text("• Published to Maven Central", font_size=24, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        bullets.move_to(ORIGIN + DOWN * 0.5)

        scene.play(LaggedStart(*[FadeIn(bullet, shift=RIGHT) for bullet in bullets], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title_group), FadeOut(bullets))

    @staticmethod
    def construct_isomsg_composite(scene):
        """ISOMsg uses Composite pattern (20-25s)."""
        # Title
        title = Text("ISOMsg & the Composite Pattern", font_size=38, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Root component
        root_label = Text("ISOComponent", font_size=26, color=COLOR_COMPOSITE, weight=BOLD)
        root_box = SurroundingRectangle(root_label, color=COLOR_COMPOSITE, buff=0.25)
        root = VGroup(root_box, root_label)
        root.move_to(UP * 2)

        scene.play(Create(root_box), Write(root_label))
        scene.wait(0.5)

        # Composite node (ISOMsg)
        composite_label = Text("ISOMsg", font_size=28, color=COLOR_ISOMSG, weight=BOLD)
        composite_sublabel = Text("(composite)", font_size=18, color=GRAY, slant=ITALIC)
        composite_sublabel.next_to(composite_label, DOWN, buff=0.1)
        composite_content = VGroup(composite_label, composite_sublabel)
        composite_box = SurroundingRectangle(composite_content, color=COLOR_ISOMSG, buff=0.25)
        composite = VGroup(composite_box, composite_content)
        composite.move_to(LEFT * 3 + DOWN * 0.5)

        # Leaf nodes
        leaf1_label = Text("ISOField", font_size=24, color=COLOR_ISOMSG)
        leaf1_box = SurroundingRectangle(leaf1_label, color=COLOR_ISOMSG, buff=0.2)
        leaf1 = VGroup(leaf1_box, leaf1_label)
        leaf1.move_to(RIGHT * 1 + DOWN * 0.5)

        leaf2_label = Text("ISOBitMapField", font_size=24, color=COLOR_ISOMSG)
        leaf2_box = SurroundingRectangle(leaf2_label, color=COLOR_ISOMSG, buff=0.2)
        leaf2 = VGroup(leaf2_box, leaf2_label)
        leaf2.next_to(leaf1, RIGHT, buff=0.8)

        # Draw tree connections
        line1 = Line(root.get_bottom(), composite.get_top(), color=GRAY)
        line2 = Line(root.get_bottom(), leaf1.get_top(), color=GRAY)
        line3 = Line(root.get_bottom(), leaf2.get_top(), color=GRAY)

        scene.play(Create(line1), Create(line2), Create(line3), run_time=0.8)
        scene.play(Create(composite_box), Write(composite_content))
        scene.play(Create(leaf1_box), Write(leaf1_label))
        scene.play(Create(leaf2_box), Write(leaf2_label))
        scene.wait(0.5)

        # Pulse composite vs leaves
        scene.play(Indicate(composite, color=YELLOW, scale_factor=1.1))
        scene.play(Indicate(leaf1, color=WHITE, scale_factor=1.05), Indicate(leaf2, color=WHITE, scale_factor=1.05))
        scene.wait(0.5)

        # Clear for code demo
        scene.play(FadeOut(root), FadeOut(composite), FadeOut(leaf1), FadeOut(leaf2),
                  FadeOut(line1), FadeOut(line2), FadeOut(line3))

        # Code example overlay
        code_lines = VGroup(
            Text('ISOMsg m = new ISOMsg();', font_size=26, font="monospace", color=COLOR_ISOMSG),
            Text('m.setMTI("0800");', font_size=26, font="monospace", color=COLOR_ISOMSG),
            Text('m.set(3, "000000");', font_size=26, font="monospace", color=COLOR_ISOMSG),
            Text('m.set(11, "000001");', font_size=26, font="monospace", color=COLOR_ISOMSG),
            Text('m.set(41, "29110001");', font_size=26, font="monospace", color=COLOR_ISOMSG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        code_lines.move_to(ORIGIN)

        scene.play(LaggedStart(*[FadeIn(line, shift=RIGHT) for line in code_lines], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title), FadeOut(code_lines))

    @staticmethod
    def construct_packager_concept(scene):
        """Packagers in Action (30-35s)."""
        # Phase 1: Introduction
        title = Text("Packagers in Action", font_size=42, weight=BOLD, color=COLOR_PACKAGER)
        subtitle = Text("Watch how packagers transform ISOMsg fields into bytes", font_size=24)
        subtitle.next_to(title, DOWN, buff=0.3)

        title_group = VGroup(title, subtitle)
        title_group.move_to(ORIGIN)

        scene.play(FadeIn(title, shift=UP), run_time=0.8)
        scene.play(FadeIn(subtitle), run_time=0.5)
        scene.wait(1)
        scene.play(title_group.animate.scale(0.7).to_edge(UP))

        # Phase 2: Show XML Packager Configuration (left side)
        xml_lines = [
            '<isopackager>',
            '  <isofield id="0" class="IFB_NUMERIC"',
            '            length="4" name="MTI"/>',
            '  <isofield id="3" class="IFB_NUMERIC"',
            '            length="6" name="Processing Code"/>',
            '  <isofield id="11" class="IFB_NUMERIC"',
            '            length="6" name="STAN"/>',
            '  <isofield id="41" class="IFA_NUMERIC"',
            '            length="8" name="Terminal ID"/>',
            '</isopackager>',
        ]

        xml_display = VGroup()
        for line in xml_lines:
            text = Text(line, font_size=16, font="monospace", color=COLOR_XML)
            xml_display.add(text)
        xml_display.arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        xml_display.move_to(LEFT * 4.3 + UP * 0.5)
        xml_display.scale(0.85)

        # Background box for XML
        xml_box = SurroundingRectangle(xml_display, color=COLOR_XML, buff=0.2, stroke_width=2)
        xml_group = VGroup(xml_box, xml_display)

        scene.play(Create(xml_box), run_time=0.5)
        scene.play(LaggedStart(*[FadeIn(line, shift=RIGHT) for line in xml_display], lag_ratio=0.08))
        scene.wait(0.5)

        # Phase 3: Show ISOMsg Code (right side)
        code_lines = VGroup(
            Text('ISOMsg m = new ISOMsg();', font_size=18, font="monospace", color=COLOR_ISOMSG),
            Text('m.setMTI("0800");', font_size=18, font="monospace", color=COLOR_ISOMSG),
            Text('m.set(3, "123456");', font_size=18, font="monospace", color=COLOR_ISOMSG),
            Text('m.set(11, "000001");', font_size=18, font="monospace", color=COLOR_ISOMSG),
            Text('m.set(41, "29110001");', font_size=18, font="monospace", color=COLOR_ISOMSG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        code_lines.move_to(RIGHT * 4.5 + UP * 0.5)

        # Background box for code
        code_box = SurroundingRectangle(code_lines, color=COLOR_ISOMSG, buff=0.2, stroke_width=2)
        code_group = VGroup(code_box, code_lines)

        scene.play(Create(code_box), run_time=0.5)
        scene.play(LaggedStart(*[FadeIn(line, shift=LEFT) for line in code_lines], lag_ratio=0.15))
        scene.wait(0.5)

        # Output strip at bottom (initially empty)
        output_label = Text("Packed bytes:", font_size=20, color=WHITE)
        output_label.to_edge(DOWN, buff=1.5).to_edge(LEFT, buff=1)
        scene.play(FadeIn(output_label))

        output_bytes = VGroup()
        # Position bytes to the right of the label
        output_position = output_label.get_right() + RIGHT * 0.5

        # Phase 4: Transform each field
        # Field 0: MTI (BCD)
        xml_highlight = SurroundingRectangle(VGroup(xml_display[1], xml_display[2]), color=ORANGE, buff=0.1, stroke_width=3)
        code_highlight = SurroundingRectangle(code_lines[1], color=YELLOW, buff=0.1, stroke_width=3)

        scene.play(Create(xml_highlight), run_time=0.4)
        scene.play(Create(code_highlight), run_time=0.4)
        scene.wait(0.3)

        T_ORIGIN = ORIGIN +np.array((0.15, 0.0, 0.0))

        # Transformation in center
        input_val = Text('"0800"', font_size=36, color=GREEN, weight=BOLD)
        input_val.move_to(T_ORIGIN + np.array((0.1, 0.0, 0.0)) + UP * 1.2)

        arrow = Text("↓", font_size=40)
        arrow.next_to(input_val, DOWN, buff=0.2)

        packager_label = Text("IFB_NUMERIC (BCD)", font_size=22, color=COLOR_PACKAGER)
        packager_label.next_to(arrow, DOWN, buff=0.2)

        output_val = Text("08 00", font_size=36, font="monospace", color=BLUE, weight=BOLD)
        output_val.next_to(packager_label, DOWN, buff=0.3)

        byte_count = Text("2 bytes", font_size=18, color=GRAY)
        byte_count.next_to(output_val, DOWN, buff=0.2)

        scene.play(FadeIn(input_val, shift=DOWN))
        scene.play(FadeIn(arrow), FadeIn(packager_label))
        scene.play(FadeIn(output_val, shift=DOWN), FadeIn(byte_count))
        scene.wait(0.5)

        # Add to output strip
        output_bytes_mti = Text("08 00", font_size=20, font="monospace", color=BLUE, weight=BOLD)
        output_bytes_mti.move_to(output_position)
        output_bytes.add(output_bytes_mti)

        # Animate bytes moving to output and highlight
        scene.play(
            ReplacementTransform(output_val.copy(), output_bytes_mti),
            run_time=0.8
        )
        highlight_rect = SurroundingRectangle(output_bytes_mti, color=YELLOW, buff=0.1)
        scene.play(Create(highlight_rect), run_time=0.3)
        scene.play(FadeOut(highlight_rect), run_time=0.3)

        # Clear transformation area
        scene.play(FadeOut(input_val), FadeOut(arrow), FadeOut(packager_label),
                  FadeOut(output_val), FadeOut(byte_count),
                  FadeOut(xml_highlight), FadeOut(code_highlight), run_time=0.3)

        # Field 3: Processing Code (BCD)
        xml_highlight = SurroundingRectangle(VGroup(xml_display[3], xml_display[4]), color=ORANGE, buff=0.1, stroke_width=3)
        code_highlight = SurroundingRectangle(code_lines[2], color=YELLOW, buff=0.1, stroke_width=3)

        scene.play(Create(xml_highlight), Create(code_highlight), run_time=0.4)

        input_val = Text('"123456"', font_size=36, color=GREEN, weight=BOLD)
        input_val.move_to(T_ORIGIN + UP * 1.2)
        arrow = Text("↓", font_size=40)
        arrow.next_to(input_val, DOWN, buff=0.2)
        packager_label = Text("IFB_NUMERIC (BCD)", font_size=22, color=COLOR_PACKAGER)
        packager_label.next_to(arrow, DOWN, buff=0.2)
        output_val = Text("12 34 56", font_size=36, font="monospace", color=BLUE, weight=BOLD)
        output_val.next_to(packager_label, DOWN, buff=0.3)
        byte_count = Text("3 bytes", font_size=18, color=GRAY)
        byte_count.next_to(output_val, DOWN, buff=0.2)

        scene.play(FadeIn(input_val, shift=DOWN))
        scene.play(FadeIn(arrow), FadeIn(packager_label))
        scene.play(FadeIn(output_val, shift=DOWN), FadeIn(byte_count))
        scene.wait(0.5)

        # Add to output strip
        output_bytes_f3 = Text("12 34 56", font_size=20, font="monospace", color=BLUE, weight=BOLD)
        output_bytes_f3.next_to(output_bytes_mti, RIGHT, buff=0.3)
        output_bytes.add(output_bytes_f3)

        # Animate and highlight
        scene.play(
            ReplacementTransform(output_val.copy(), output_bytes_f3),
            run_time=0.8
        )
        highlight_rect = SurroundingRectangle(output_bytes_f3, color=YELLOW, buff=0.1)
        scene.play(Create(highlight_rect), run_time=0.3)
        scene.play(FadeOut(highlight_rect), run_time=0.3)

        scene.play(FadeOut(input_val), FadeOut(arrow), FadeOut(packager_label),
                  FadeOut(output_val), FadeOut(byte_count),
                  FadeOut(xml_highlight), FadeOut(code_highlight), run_time=0.3)

        # Field 11: STAN (BCD)
        xml_highlight = SurroundingRectangle(VGroup(xml_display[5], xml_display[6]), color=ORANGE, buff=0.1, stroke_width=3)
        code_highlight = SurroundingRectangle(code_lines[3], color=YELLOW, buff=0.1, stroke_width=3)

        scene.play(Create(xml_highlight), Create(code_highlight), run_time=0.4)

        input_val = Text('"000001"', font_size=36, color=GREEN, weight=BOLD)
        input_val.move_to(T_ORIGIN + UP * 1.2)
        arrow = Text("↓", font_size=40)
        arrow.next_to(input_val, DOWN, buff=0.2)
        packager_label = Text("IFB_NUMERIC (BCD)", font_size=22, color=COLOR_PACKAGER)
        packager_label.next_to(arrow, DOWN, buff=0.2)
        output_val = Text("00 00 01", font_size=36, font="monospace", color=BLUE, weight=BOLD)
        output_val.next_to(packager_label, DOWN, buff=0.3)
        byte_count = Text("3 bytes", font_size=18, color=GRAY)
        byte_count.next_to(output_val, DOWN, buff=0.2)

        scene.play(FadeIn(input_val, shift=DOWN))
        scene.play(FadeIn(arrow), FadeIn(packager_label))
        scene.play(FadeIn(output_val, shift=DOWN), FadeIn(byte_count))
        scene.wait(0.5)

        # Add to output strip
        output_bytes_f11 = Text("00 00 01", font_size=20, font="monospace", color=BLUE, weight=BOLD)
        output_bytes_f11.next_to(output_bytes_f3, RIGHT, buff=0.3)
        output_bytes.add(output_bytes_f11)

        # Animate and highlight
        scene.play(
            ReplacementTransform(output_val.copy(), output_bytes_f11),
            run_time=0.8
        )
        highlight_rect = SurroundingRectangle(output_bytes_f11, color=YELLOW, buff=0.1)
        scene.play(Create(highlight_rect), run_time=0.3)
        scene.play(FadeOut(highlight_rect), run_time=0.3)

        scene.play(FadeOut(input_val), FadeOut(arrow), FadeOut(packager_label),
                  FadeOut(output_val), FadeOut(byte_count),
                  FadeOut(xml_highlight), FadeOut(code_highlight), run_time=0.3)

        # Field 41: Terminal ID (ASCII - contrast!)
        xml_highlight = SurroundingRectangle(VGroup(xml_display[7], xml_display[8]), color=ORANGE, buff=0.1, stroke_width=3)
        code_highlight = SurroundingRectangle(code_lines[4], color=YELLOW, buff=0.1, stroke_width=3)

        scene.play(Create(xml_highlight), Create(code_highlight), run_time=0.4)

        input_val = Text('"29110001"', font_size=36, color=GREEN, weight=BOLD)
        input_val.move_to(T_ORIGIN + UP * 1.2)
        arrow = Text("↓", font_size=40)
        arrow.next_to(input_val, DOWN, buff=0.2)
        packager_label = Text("IFA_NUMERIC (ASCII)", font_size=22, color=COLOR_PACKAGER, weight=BOLD)
        packager_label.next_to(arrow, DOWN, buff=0.2)
        output_val = Text("32 39 31 31 30 30 30 31", font_size=16, font="monospace", color=GREEN, weight=BOLD)
        output_val.next_to(packager_label, DOWN, buff=0.3)
        byte_count = Text("8 bytes (1 byte per digit!)", font_size=18, color=YELLOW)
        byte_count.next_to(output_val, DOWN, buff=0.2)

        scene.play(FadeIn(input_val, shift=DOWN))
        scene.play(FadeIn(arrow), FadeIn(packager_label))
        scene.play(FadeIn(output_val, shift=DOWN), FadeIn(byte_count))
        scene.wait(0.8)

        # Add to output strip
        output_bytes_f41 = Text("32 39 31 31 30 30 30 31", font_size=20, font="monospace", color=GREEN, weight=BOLD)
        output_bytes_f41.next_to(output_bytes_f11, RIGHT, buff=0.3)
        output_bytes.add(output_bytes_f41)

        # Animate and highlight
        scene.play(
            ReplacementTransform(output_val.copy(), output_bytes_f41),
            run_time=0.8
        )
        highlight_rect = SurroundingRectangle(output_bytes_f41, color=YELLOW, buff=0.1)
        scene.play(Create(highlight_rect), run_time=0.3)
        scene.play(FadeOut(highlight_rect), run_time=0.3)

        scene.play(FadeOut(input_val), FadeOut(arrow), FadeOut(packager_label),
                  FadeOut(output_val), FadeOut(byte_count),
                  FadeOut(xml_highlight), FadeOut(code_highlight), run_time=0.3)

        # Phase 5: Show complete message
        total_bytes = Text("Total: 16 bytes (2+3+3+8)", font_size=24, color=YELLOW, weight=BOLD)
        total_bytes.move_to(ORIGIN + DOWN * 0.5 + RIGHT * 0.15)

        comparison = VGroup(
            Text("IFB (BCD): 2 digits per byte", font_size=20, color=BLUE),
            Text("IFA (ASCII): 1 digit per byte", font_size=20, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        comparison.next_to(total_bytes, DOWN, buff=0.5)

        scene.play(FadeIn(total_bytes, shift=UP))
        scene.play(Indicate(output_bytes, color=YELLOW, scale_factor=1.05))
        scene.wait(0.5)
        scene.play(FadeIn(comparison, shift=UP))
        scene.wait(2)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

    @staticmethod
    def construct_packager_definition(scene):
        """Defining a Packager (15-20s)."""
        # Title
        title = Text("Packager Configuration", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # XML snippet
        xml_lines = [
            '<isopackager>',
            '  <isofield id="0" length="4" name="MESSAGE TYPE INDICATOR" class="org.jpos.iso.IFB_NUMERIC" />',
            '  <isofield id="3" length="6" name="PROCESSING CODE" class="org.jpos.iso.IFB_NUMERIC" />',
            '  <isofield id="11" length="6" name="STAN" class="org.jpos.iso.IFB_NUMERIC" />',
            '  <isofield id="41" length="8" name="TERMINAL ID" class="org.jpos.iso.IFA_NUMERIC" />',
            '</isopackager>',
        ]

        xml_display = VGroup()
        for line in xml_lines:
            text = Text(line, font_size=14, font="monospace", color=COLOR_XML)
            xml_display.add(text)
        xml_display.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        xml_display.scale(1.1)
        xml_display.move_to(ORIGIN + UP * 0.2)

        scene.play(LaggedStart(*[FadeIn(line, shift=RIGHT) for line in xml_display], lag_ratio=0.1))
        scene.wait(0.5)

        # Highlight key field lines (one line per field now)
        highlights = []
        for i in [1, 2, 3, 4]:  # Field definitions at indices 1-4
            rect = SurroundingRectangle(xml_display[i], color=YELLOW, buff=0.1)
            highlights.append(rect)

        for i, rect in enumerate(highlights):
            if i == 0:
                scene.play(Create(rect), run_time=0.5)
            else:
                scene.play(ReplacementTransform(highlights[i-1], rect), run_time=0.5)
            scene.wait(2)  # 2 seconds per field
        scene.play(FadeOut(highlights[-1]))
        scene.wait(0.5)

        # Caption
        caption = Text("GenericPackager: XML-based configuration", font_size=26, color=COLOR_PACKAGER)
        caption.to_edge(DOWN, buff=1)
        scene.play(FadeIn(caption, shift=UP))
        scene.wait(1)

        # Alternative badge
        alt_badge = Text("Or extend ISOBasePackager in Java", font_size=24, color=GRAY, slant=ITALIC)
        alt_badge.next_to(caption, DOWN, buff=0.3)
        scene.play(FadeIn(alt_badge))
        scene.wait(1)
        scene.play(FadeOut(title), FadeOut(xml_display), FadeOut(caption), FadeOut(alt_badge))

    @staticmethod
    def construct_composite_subfields(scene):
        """Composite subfields - DE 3 (25-35s)."""
        # Title
        title = Text("Composite Subfields: DE 3 Example", font_size=38, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # LEFT SIDE: DE 3 label at top
        de3_label = Text("DE 3: Processing Code (N 6)", font_size=26, color=COLOR_DATA_ELEMENT, weight=BOLD)
        de3_box = SurroundingRectangle(de3_label, color=COLOR_DATA_ELEMENT, buff=0.25)
        de3_group = VGroup(de3_box, de3_label)
        de3_group.move_to(LEFT * 3.5 + UP * 1.8)

        scene.play(Create(de3_box), Write(de3_label))
        scene.wait(0.8)

        # LEFT SIDE: 3 subfields with aligned '=' signs
        subfield1_text = Text("Transaction Code(2)  = \"01\"", font_size=20, font="monospace", color=GREEN)
        subfield1_box = SurroundingRectangle(subfield1_text, color=GREEN, buff=0.2)
        subfield1 = VGroup(subfield1_box, subfield1_text)
        subfield1.next_to(de3_group, DOWN, buff=0.6)

        subfield2_text = Text("Account-From(2)      = \"02\"", font_size=20, font="monospace", color=GREEN)
        subfield2_box = SurroundingRectangle(subfield2_text, color=GREEN, buff=0.2)
        subfield2 = VGroup(subfield2_box, subfield2_text)
        subfield2.next_to(subfield1, DOWN, buff=0.5)

        subfield3_text = Text("Account-To(2)        = \"03\"", font_size=20, font="monospace", color=GREEN)
        subfield3_box = SurroundingRectangle(subfield3_text, color=GREEN, buff=0.2)
        subfield3 = VGroup(subfield3_box, subfield3_text)
        subfield3.next_to(subfield2, DOWN, buff=0.5)

        # Animate explosion
        scene.play(
            FadeIn(subfield1, shift=DOWN),
            FadeIn(subfield2, shift=DOWN),
            FadeIn(subfield3, shift=DOWN),
            de3_group.animate.scale(0.8),
            run_time=1.2
        )
        scene.wait(0.5)

        # RIGHT SIDE: XML packager configuration
        xml_snippet = VGroup(
            Text('<isofield id="3" name="PROCESSING CODE"', font_size=18, font="monospace", color=COLOR_XML),
            Text('  packager="GenericSubFieldPackager">', font_size=18, font="monospace", color=COLOR_XML),
            Text('    <isofield id="1" length="2" name="TX_CODE" />', font_size=18, font="monospace", color=COLOR_XML),
            Text('    <isofield id="2" length="2" name="ACCT_FROM" />', font_size=18, font="monospace", color=COLOR_XML),
            Text('    <isofield id="3" length="2" name="ACCT_TO" />', font_size=18, font="monospace", color=COLOR_XML),
            Text('</isofield>', font_size=18, font="monospace", color=COLOR_XML),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        xml_snippet.move_to(RIGHT * 3.5 + UP * 1.2)

        scene.play(FadeIn(xml_snippet, shift=LEFT))
        scene.wait(1)

        # RIGHT SIDE: Code example below XML
        code_example = VGroup(
            Text('msg.set(3, 1, "01");', font_size=18, font="monospace", color=COLOR_ISOMSG),
            Text('msg.set(3, 2, "02");', font_size=18, font="monospace", color=COLOR_ISOMSG),
            Text('msg.set(3, 3, "03");', font_size=18, font="monospace", color=COLOR_ISOMSG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        # Background box for code
        code_box = SurroundingRectangle(code_example, color=COLOR_ISOMSG, buff=0.2, stroke_width=2)
        code_group = VGroup(code_box, code_example)
        code_group.next_to(xml_snippet, DOWN, buff=0.5)

        scene.play(Create(code_box), FadeIn(code_example, shift=UP))
        scene.wait(1)

        # Bottom: Recombination result (centered, at the very bottom)
        combined = Text("Packed: 010203 → 01 02 03 (3 BCD bytes)", font_size=24, color=COLOR_DATA_ELEMENT, weight=BOLD)
        combined.to_edge(DOWN, buff=0.8)

        scene.play(FadeIn(combined, shift=UP))
        scene.wait(2)
        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

    @staticmethod
    def construct_byte_packing(scene):
        """Byte-by-byte packing vignette (30-40s)."""
        # Title
        title = Text("Encoding in Action", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Cut 1 - MTI encoding comparison
        cut1_title = Text("MTI Encoding", font_size=32, color=COLOR_MTI, weight=BOLD)
        cut1_title.move_to(UP * 2)

        ascii_encoding = VGroup(
            Text("IFA_NUMERIC (ASCII)", font_size=24, color=COLOR_PACKAGER),
            Text('"0100" → 30 31 30 30 (4 bytes)', font_size=26, font="monospace", color=GREEN),
        ).arrange(DOWN, buff=0.3)
        ascii_encoding.move_to(UP * 0.8)

        bcd_encoding = VGroup(
            Text("IFB_NUMERIC (BCD)", font_size=24, color=COLOR_PACKAGER),
            Text('"0100" → 01 00 (2 bytes)', font_size=26, font="monospace", color=YELLOW),
        ).arrange(DOWN, buff=0.3)
        bcd_encoding.move_to(DOWN * 0.5)

        scene.play(Write(cut1_title))
        scene.play(FadeIn(ascii_encoding, shift=RIGHT))
        scene.wait(0.5)
        scene.play(Indicate(ascii_encoding[1], color=WHITE, scale_factor=1.1))
        scene.wait(0.8)
        scene.play(FadeIn(bcd_encoding, shift=RIGHT))
        scene.wait(0.5)
        scene.play(Indicate(bcd_encoding[1], color=WHITE, scale_factor=1.1))
        scene.wait(0.8)
        scene.play(FadeOut(cut1_title), FadeOut(ascii_encoding), FadeOut(bcd_encoding))

        # LLVAR packing
        cut3_title = Text("DE 2 LLVAR Packing", font_size=32, color=COLOR_DATA_ELEMENT, weight=BOLD)
        cut3_title.move_to(UP * 2)

        # Create the full encoded line with proper spacing
        encoded_full = Text("Encoded: 16 45 39 68 12 34 56 78 90", font_size=22, font="monospace")

        # Color the "16" part in yellow, rest in green/white
        encoded_full[0:8].set_color(WHITE)  # "Encoded:"
        encoded_full[8:10].set_color(YELLOW)  # "16"
        encoded_full[8:10].set_weight(BOLD)  # Make "16" bold
        encoded_full[10:].set_color(GREEN)  # Rest of the hex bytes

        llvar_packing = VGroup(
            Text('"4539681234567890" (16 digits)', font_size=24),
            Text("↓", font_size=30),
            encoded_full,
        ).arrange(DOWN, buff=0.3)
        llvar_packing.move_to(ORIGIN)

        target_digit = encoded_full[9]

        # Add length annotation below, positioned under the "16"
        # The "16" starts at character index 9, so we align under that
        length_annotation = Text("   └─ Length (1 byte BCD)", font_size=20, color=YELLOW)
        length_annotation.next_to(encoded_full, DOWN, buff=0.2)
        length_annotation.align_to(target_digit, LEFT)
        llvar_packing.add(length_annotation)

        scene.play(Write(cut3_title))
        scene.play(LaggedStart(*[FadeIn(item, shift=DOWN) for item in llvar_packing], lag_ratio=0.3))
        scene.wait(2)
        scene.play(FadeOut(title), *[FadeOut(mob) for mob in scene.mobjects[1:]])

    @staticmethod
    def construct_channels(scene):
        """Channels (50-55s)."""
        # Title
        title = Text("Channels: Wire Protocol Adapters", font_size=38, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Section 1: ISOChannel Interface (8s)
        interface_title = Text("ISOChannel Interface", font_size=30, color=COLOR_CHANNEL, weight=BOLD)
        interface_title.move_to(UP * 2.2)

        interface_methods = VGroup(
            Text("send(ISOMsg)", font_size=24, font="monospace", color=COLOR_ISOMSG),
            Text("receive() → ISOMsg", font_size=24, font="monospace", color=COLOR_ISOMSG),
            Text("setPackager(ISOPackager)", font_size=24, font="monospace", color=COLOR_PACKAGER),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        interface_methods.move_to(UP * 0.8)

        tagline = Text("Abstracts the wire protocol", font_size=26, color=YELLOW, slant=ITALIC)
        tagline.next_to(interface_methods, DOWN, buff=0.6)

        scene.play(FadeOut(title))  # Fade out main title
        scene.play(Write(interface_title))
        scene.play(LaggedStart(*[FadeIn(method, shift=RIGHT) for method in interface_methods], lag_ratio=0.3))
        scene.play(FadeIn(tagline, shift=UP))
        scene.wait(1.5)
        scene.play(FadeOut(interface_title), FadeOut(interface_methods), FadeOut(tagline))

        # Section 2: Common Channel Types (12s)
        channels_title = Text("Common jPOS Channels", font_size=32, weight=BOLD)
        channels_title.to_edge(UP, buff=0.8)
        scene.play(Write(channels_title))

        channel_types = VGroup(
            VGroup(
                Text("NACChannel", font_size=26, color=COLOR_CHANNEL, weight=BOLD),
                Text("— Network Application Channel", font_size=22, color=GRAY)
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("BASE24Channel", font_size=26, color=COLOR_CHANNEL, weight=BOLD),
                Text("— ACI BASE24 protocol", font_size=22, color=GRAY)
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("ASCIIChannel", font_size=26, color=COLOR_CHANNEL, weight=BOLD),
                Text("— ASCII with 4-byte length header", font_size=22, color=GRAY)
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("XMLChannel", font_size=26, color=COLOR_CHANNEL, weight=BOLD),
                Text("— XML-formatted messages", font_size=22, color=GRAY)
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("LoopbackChannel", font_size=26, color=GRAY, weight=BOLD),
                Text("— Testing and simulation", font_size=22, color=GRAY)
            ).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        channel_types.move_to(ORIGIN + DOWN * 0.2)

        scene.play(LaggedStart(*[FadeIn(ch, shift=RIGHT) for ch in channel_types], lag_ratio=0.25))
        scene.wait(2.5)
        scene.play(FadeOut(channels_title), FadeOut(channel_types))

        # Section 3: Channel Components (10s)
        components_title = Text("Channel Components", font_size=32, weight=BOLD)
        components_title.to_edge(UP, buff=0.8)
        scene.play(Write(components_title))

        # Center: Channel box
        channel_box = Rectangle(width=2.5, height=1.2, color=COLOR_CHANNEL, stroke_width=3)
        channel_label = Text("Channel", font_size=26, color=COLOR_CHANNEL, weight=BOLD)
        channel_label.move_to(channel_box.get_center())
        channel_group = VGroup(channel_box, channel_label)
        channel_group.move_to(ORIGIN)

        # Packager component (left)
        packager_label = Text("Packager", font_size=22, color=COLOR_PACKAGER, weight=BOLD)
        packager_desc = Text("ISOMsg ↔ bytes", font_size=18, color=COLOR_PACKAGER)
        packager_desc.next_to(packager_label, DOWN, buff=0.2)
        packager_group = VGroup(packager_label, packager_desc)
        packager_group.move_to(LEFT * 4 + UP * 0.5)

        # Endpoint component (right top)
        endpoint_label = Text("Endpoint", font_size=22, color=BLUE, weight=BOLD)
        endpoint_desc = Text("host:port", font_size=18, color=BLUE)
        endpoint_desc.next_to(endpoint_label, DOWN, buff=0.2)
        endpoint_group = VGroup(endpoint_label, endpoint_desc)
        endpoint_group.move_to(RIGHT * 4 + UP * 0.5)

        # Filters component (right bottom)
        filters_label = Text("Filters", font_size=22, color=YELLOW, weight=BOLD)
        filters_desc = Text("incoming/outgoing", font_size=18, color=YELLOW)
        filters_desc.next_to(filters_label, DOWN, buff=0.2)
        filters_group = VGroup(filters_label, filters_desc)
        filters_group.move_to(RIGHT * 4 + DOWN * 1.2)

        # Connection lines
        line1 = Line(channel_box.get_left(), packager_group.get_right(), color=GRAY)
        line2 = Line(channel_box.get_right(), endpoint_group.get_left(), color=GRAY)
        line3 = Line(channel_box.get_right() + DOWN * 0.3, filters_group.get_left(), color=GRAY)

        scene.play(Create(channel_box), Write(channel_label))
        scene.play(Create(line1), FadeIn(packager_group, shift=RIGHT))
        scene.play(Create(line2), FadeIn(endpoint_group, shift=LEFT))
        scene.play(Create(line3), FadeIn(filters_group, shift=LEFT))
        scene.wait(2)
        scene.play(FadeOut(components_title), FadeOut(channel_group), FadeOut(packager_group),
                  FadeOut(endpoint_group), FadeOut(filters_group),
                  FadeOut(line1), FadeOut(line2), FadeOut(line3))

        # Section 4: Code Example (15s)
        code_title = Text("Send & Receive", font_size=32, weight=BOLD)
        code_title.to_edge(UP, buff=0.8)
        scene.play(Write(code_title))

        code_lines = VGroup(
            Text('ISOChannel channel = new NACChannel(', font_size=20, font="monospace", color=COLOR_CHANNEL),
            Text('    host, port, packager', font_size=20, font="monospace", color=GRAY),
            Text(');', font_size=20, font="monospace", color=WHITE),
            Text('channel.connect();', font_size=20, font="monospace", color=COLOR_CHANNEL),
            Text('channel.send(msg);', font_size=20, font="monospace", color=COLOR_ISOMSG),
            Text('ISOMsg response = channel.receive();', font_size=20, font="monospace", color=COLOR_ISOMSG),
            Text('channel.disconnect();', font_size=20, font="monospace", color=COLOR_CHANNEL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        code_lines.move_to(ORIGIN)

        # Comment annotations
        send_comment = Text("// Send request", font_size=18, color=GREEN, slant=ITALIC)
        send_comment.next_to(code_lines[4], RIGHT, buff=0.5)

        receive_comment = Text("// Wait for response", font_size=18, color=GREEN, slant=ITALIC)
        receive_comment.next_to(code_lines[5], RIGHT, buff=0.5)

        scene.play(LaggedStart(*[FadeIn(line, shift=RIGHT) for line in code_lines], lag_ratio=0.3))
        scene.wait(0.5)
        scene.play(FadeIn(send_comment, shift=LEFT))
        scene.play(FadeIn(receive_comment, shift=LEFT))
        scene.wait(2.5)
        scene.play(FadeOut(code_title), FadeOut(code_lines), FadeOut(send_comment), FadeOut(receive_comment))

        # Section 5: Message Flow Animation (10s)
        # Client and Server
        client = Text("Client", font_size=28)
        client.move_to(LEFT * 5 + UP * 0.5)

        server = Text("Server", font_size=28)
        server.move_to(RIGHT * 5 + UP * 0.5)

        # Socket line
        socket_line = Line(LEFT * 4 + UP * 0.5, RIGHT * 4 + UP * 0.5, color=COLOR_CHANNEL, stroke_width=4)

        # Method labels
        send_label = Text("channel.send(msg)", font_size=20, color=COLOR_ISOMSG)
        send_label.next_to(client, DOWN, buff=0.5)

        receive_label = Text("channel.receive()", font_size=20, color=COLOR_ISOMSG)
        receive_label.next_to(server, DOWN, buff=0.5)

        scene.play(Write(client), Write(server), Create(socket_line))
        scene.play(FadeIn(send_label), FadeIn(receive_label))
        scene.wait(0.5)

        # Message packet animation
        message_packet = Square(side_length=1.5, color=GREEN, fill_opacity=0.7)
        msg_label = Text("ISOMsg", font_size=24, color=WHITE, weight=BOLD)
        msg_label.move_to(message_packet.get_center())
        msg_group = VGroup(message_packet, msg_label)
        msg_group.move_to(socket_line.get_start())

        scene.play(msg_group.animate.move_to(socket_line.get_end()), run_time=2, rate_func=linear)
        scene.wait(1)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

    @staticmethod
    def construct_qmux(scene):
        """QMUX - Multiplexing (60-90s comprehensive)."""

        # Helper function to create message box with details
        def create_message_box(label, mti, de41, de11, color=GREEN):
            box = Rectangle(width=1.5, height=1.2, color=color, fill_opacity=0.3, stroke_width=2)
            msg_label = Text(label, font_size=18, weight=BOLD, color=WHITE)
            mti_text = Text(f"MTI:{mti}", font_size=14, font="monospace")
            key_text = Text(f"{de41}|{de11}", font_size=12, font="monospace", color=YELLOW)

            content = VGroup(msg_label, mti_text, key_text).arrange(DOWN, buff=0.1)
            content.move_to(box.get_center())
            return VGroup(box, content)

        # Helper function to create key tag
        def create_key_tag(key_str, color="#FF6B35"):
            tag = Rectangle(width=len(key_str)*0.12, height=0.3, color=color, fill_opacity=0.7, stroke_width=1)
            tag_text = Text(key_str, font_size=12, color=WHITE)
            tag_text.move_to(tag.get_center())
            return VGroup(tag, tag_text)

        # Helper function to create thread indicator
        def create_thread_indicator(name, state="active"):
            colors = {"active": GREEN, "waiting": YELLOW, "done": GRAY}
            circle = Circle(radius=0.25, color=colors.get(state, GREEN), fill_opacity=0.6, stroke_width=2)
            label = Text(name, font_size=16, weight=BOLD)
            label.move_to(circle.get_center())
            return VGroup(circle, label)

        # Helper function to create queue visualization
        def create_queue_viz(title, num_slots=3, color=ORANGE):
            slots = VGroup(*[
                Rectangle(width=1.8, height=0.8, color=color, stroke_width=2)
                for _ in range(num_slots)
            ]).arrange(DOWN, buff=0.15)
            queue_title = Text(title, font_size=20, color=color, weight=BOLD)
            queue_title.next_to(slots, UP, buff=0.3)
            return VGroup(queue_title, slots)

        # =======================================================================
        # SECTION 1: The Problem (10-12s)
        # =======================================================================
        section1_title = Text("The Problem: One Socket, Many Threads", font_size=40, weight=BOLD)
        section1_title.to_edge(UP, buff=0.4)
        scene.play(Write(section1_title), run_time=0.6)

        # Emphasis on single socket constraint - bigger text
        constraint_text = Text("Only ONE socket connection to processor", font_size=26, color=YELLOW, weight=BOLD)
        constraint_text.next_to(section1_title, DOWN, buff=0.3)
        scene.play(FadeIn(constraint_text, shift=DOWN))
        scene.wait(0.5)

        # Split screen comparison - divider starts BELOW the constraint text
        divider = Line(UP * 1.3, DOWN * 3, color=GRAY)
        divider.move_to(ORIGIN + DOWN * 0.35)

        # Left: Without MUX (Serial) - moved down
        left_title = Text("Without Multiplexing", font_size=28, weight=BOLD, color=RED)
        left_title.move_to(LEFT * 3.5 + UP * 0.9)
        left_subtitle = Text("Serial: One at a time", font_size=20, color=GRAY, slant=ITALIC)
        left_subtitle.next_to(left_title, DOWN, buff=0.2)

        # Right: With QMUX (Concurrent) - moved down
        right_title = Text("With QMUX", font_size=28, weight=BOLD, color=GREEN)
        right_title.move_to(RIGHT * 3.5 + UP * 0.8)
        right_subtitle = Text("Concurrent: Share the socket", font_size=20, color=GRAY, slant=ITALIC)
        right_subtitle.next_to(right_title, DOWN, buff=0.2)

        scene.play(Create(divider), Write(left_title), Write(right_title))
        scene.play(FadeIn(left_subtitle), FadeIn(right_subtitle))

        DOWN_DELTA = 0.7

        # LEFT SIDE: Show single socket with serial access - moved down
        left_threads = VGroup(*[create_thread_indicator(f"T{i+1}") for i in range(3)])
        left_threads.arrange(DOWN, buff=0.4).move_to(LEFT * 5.5 + DOWN * DOWN_DELTA)

        # Single socket on left (emphasized) - moved down
        left_socket = Rectangle(width=1.5, height=0.6, color=COLOR_CHANNEL, fill_opacity=0.4, stroke_width=3)
        left_socket.move_to(LEFT * 3 + DOWN * DOWN_DELTA)
        left_socket_label = Text("SINGLE\nSOCKET", font_size=14, color=COLOR_CHANNEL, weight=BOLD)
        left_socket_label.move_to(left_socket.get_center())

        # Payment processor on left - moved down and RIGHT to avoid overlap
        left_processor = Circle(radius=0.5, color="#E6CCFF", fill_opacity=0.3, stroke_width=3)
        left_processor.move_to(LEFT * 0.8 + DOWN * DOWN_DELTA)
        left_proc_label = Text("Proc", font_size=14, color="#E6CCFF")
        left_proc_label.move_to(left_processor.get_center())

        # Connection line
        left_line = Line(left_socket.get_right(), left_processor.get_left(), color=COLOR_CHANNEL, stroke_width=2)

        scene.play(
            LaggedStart(*[FadeIn(t) for t in left_threads], lag_ratio=0.2),
            Create(left_socket), Write(left_socket_label),
            Create(left_line),
            Create(left_processor), Write(left_proc_label)
        )

        # Show T1 using socket, others blocked
        for i, thread in enumerate(left_threads):
            if i > 0:
                thread[0].set_fill(YELLOW, opacity=0.3)  # waiting

        # Add "BLOCKED" label
        blocked_label = Text("Blocked!", font_size=18, color=RED, weight=BOLD)
        blocked_label.next_to(left_threads[1], RIGHT, buff=0.3)
        scene.play(FadeIn(blocked_label))
        scene.wait(1)

        # RIGHT SIDE: Show same single socket with QMUX multiplexing - moved down
        right_threads = VGroup(*[create_thread_indicator(f"T{i+1}") for i in range(3)])
        right_threads.arrange(DOWN, buff=0.4).move_to(RIGHT * 5.5 + DOWN * DOWN_DELTA)

        # QMUX box - using ORANGE for better contrast instead of violet
        qmux_small = Rectangle(width=1.2, height=1.5, color=ORANGE, fill_opacity=0.4, stroke_width=3)
        qmux_small.move_to(RIGHT * 4 + DOWN * DOWN_DELTA)
        qmux_small_label = Text("QMUX", font_size=18, color=ORANGE, weight=BOLD)
        qmux_small_label.move_to(qmux_small.get_center())

        # Single socket on right (same constraint!) - moved down
        right_socket = Rectangle(width=1.5, height=0.6, color=COLOR_CHANNEL, fill_opacity=0.4, stroke_width=3)
        right_socket.move_to(RIGHT * 2.2 + DOWN * DOWN_DELTA)
        right_socket_label = Text("SAME\nSOCKET", font_size=14, color=COLOR_CHANNEL, weight=BOLD)
        right_socket_label.move_to(right_socket.get_center())

        # Payment processor on right - moved down and LEFT to avoid overlap
        right_processor = Circle(radius=0.5, color="#E6CCFF", fill_opacity=0.3, stroke_width=3)
        right_processor.move_to(RIGHT * 0.6 + DOWN * DOWN_DELTA)
        right_proc_label = Text("Proc", font_size=14, color="#E6CCFF")
        right_proc_label.move_to(right_processor.get_center())

        # Connection lines
        right_line1 = Line(qmux_small.get_left(), right_socket.get_right(), color=COLOR_CHANNEL, stroke_width=2)
        right_line2 = Line(right_socket.get_left(), right_processor.get_right(), color=COLOR_CHANNEL, stroke_width=2)

        scene.play(
            LaggedStart(*[FadeIn(t) for t in right_threads], lag_ratio=0.2),
            Create(qmux_small), Write(qmux_small_label),
            Create(right_socket), Write(right_socket_label),
            Create(right_line1), Create(right_line2),
            Create(right_processor), Write(right_proc_label)
        )

        # All can send - QMUX manages the shared socket
        for thread in right_threads:
            thread[0].set_fill(GREEN, opacity=0.6)  # all active

        # Add "All active!" label - moved DOWN below threads to avoid overlap with QMUX box
        active_label = Text("All active!", font_size=18, color=GREEN, weight=BOLD)
        active_label.move_to(RIGHT * 5.5 + DOWN * 2.2)
        scene.play(FadeIn(active_label))

        # Highlight the key insight - bigger text
        insight = Text("QMUX multiplexes the single socket", font_size=24, color=YELLOW, slant=ITALIC)
        insight.to_edge(DOWN, buff=0.5)
        scene.play(FadeIn(insight, shift=UP))
        scene.wait(2)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 2: Three-Layer Architecture (12-15s)
        # =======================================================================
        arch_title = Text("QMUX Architecture", font_size=36, weight=BOLD)
        arch_title.to_edge(UP, buff=0.4)
        scene.play(Write(arch_title), run_time=0.6)
        scene.wait(0.3)
        scene.play(arch_title.animate.scale(0.7).to_edge(UP, buff=0.2))

        # Application Layer (Yellow box)
        app_box = Rectangle(width=10, height=1.3, color="#FFEB99", fill_opacity=0.2, stroke_width=3)
        app_box.move_to(UP * 2.4)
        app_label = Text("APPLICATION LAYER", font_size=20, weight=BOLD, color="#FFEB99")
        app_label.move_to(app_box.get_top() + DOWN * 0.3)

        # Threads in app layer
        app_threads = VGroup(*[create_thread_indicator(f"T{i+1}", "active") for i in range(3)])
        app_threads.arrange(RIGHT, buff=0.8).scale(0.7)
        app_threads.move_to(app_box.get_center() + DOWN * 0.15)

        mux_request_label = Text("mux.request()", font_size=20, color=WHITE)
        mux_request_label.next_to(app_box, DOWN, buff=0.08)

        scene.play(Create(app_box), Write(app_label))
        scene.play(LaggedStart(*[FadeIn(t) for t in app_threads], lag_ratio=0.2))
        scene.play(FadeIn(mux_request_label, shift=DOWN))
        scene.wait(0.5)

        # jPOS Infrastructure Layer (Light blue box) - Slightly larger for better spacing
        jpos_box = Rectangle(width=10, height=3.5, color="#CCE5FF", fill_opacity=0.2, stroke_width=3)
        jpos_box.move_to(DOWN * 0.5)
        jpos_label = Text("jPOS INFRASTRUCTURE", font_size=20, weight=BOLD, color="#CCE5FF")
        jpos_label.move_to(jpos_box.get_top() + DOWN * 0.3)

        # QMUX component - ORANGE to match Section 1
        qmux_box = Rectangle(width=1.8, height=0.7, color=ORANGE, fill_opacity=0.4, stroke_width=3)
        qmux_box.move_to(jpos_box.get_top() + DOWN * 0.95)
        qmux_label = Text("QMUX", font_size=18, color=ORANGE, weight=BOLD)
        qmux_label.move_to(qmux_box.get_center())

        # Queues - ORANGE to match QMUX
        out_queue = Rectangle(width=1.1, height=1.0, color=ORANGE, stroke_width=2, fill_opacity=0.1)
        out_queue.move_to(LEFT * 3.2 + DOWN * 0.25)
        out_label = Text("Outgoing\nQueue", font_size=13, color=ORANGE)
        out_label.move_to(out_queue.get_center())

        in_queue = Rectangle(width=1.1, height=1.0, color=ORANGE, stroke_width=2, fill_opacity=0.1)
        in_queue.move_to(RIGHT * 3.2 + DOWN * 0.25)
        in_label = Text("Incoming\nQueue", font_size=13, color=ORANGE)
        in_label.move_to(in_queue.get_center())

        # ChannelAdaptor - positioned WITHIN jPOS box with proper separation
        adaptor_box = Rectangle(width=2.2, height=0.55, color=BLUE, fill_opacity=0.3, stroke_width=2)
        adaptor_box.move_to(DOWN * 0.9)
        adaptor_label = Text("ChannelAdaptor", font_size=13, color=BLUE)
        adaptor_label.move_to(adaptor_box.get_center())

        # Channel - positioned WITHIN jPOS box with clear separation from ChannelAdaptor
        channel_box = Rectangle(width=2.2, height=0.55, color=COLOR_CHANNEL, fill_opacity=0.3, stroke_width=2)
        channel_box.move_to(jpos_box.get_bottom() + UP * 0.45)
        channel_label = Text("Channel (TCP)", font_size=13, color=COLOR_CHANNEL)
        channel_label.move_to(channel_box.get_center())

        scene.play(Create(jpos_box), Write(jpos_label))
        scene.play(Create(qmux_box), Write(qmux_label))
        scene.play(
            Create(out_queue), Write(out_label),
            Create(in_queue), Write(in_label)
        )
        scene.play(Create(adaptor_box), Write(adaptor_label))
        scene.play(Create(channel_box), Write(channel_label))
        scene.wait(1)

        # Payment Processor Layer (Light purple box)
        proc_box = Rectangle(width=10, height=1.0, color="#E6CCFF", fill_opacity=0.2, stroke_width=3)
        proc_box.to_edge(DOWN, buff=0.4)
        proc_label = Text("PAYMENT PROCESSOR", font_size=20, weight=BOLD, color="#E6CCFF")
        proc_label.move_to(proc_box.get_center())

        scene.play(Create(proc_box), Write(proc_label))
        scene.wait(2)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 3: Key Concept (15-18s)
        # =======================================================================
        key_title = Text("The Correlation Key", font_size=36, weight=BOLD)
        key_title.to_edge(UP, buff=0.5)
        scene.play(Write(key_title), run_time=0.6)
        scene.wait(0.3)

        # Example message
        msg_example = VGroup(
            Text("MTI: 0200", font_size=24, color=COLOR_MTI),
            Text("DE 2: 4111111111111111", font_size=20, color=GRAY),
            Text("DE 4: 000000010000", font_size=20, color=GRAY),
            Text("DE 11: 000001", font_size=24, color="#FF6B35", weight=BOLD),
            Text("DE 41: 29110001", font_size=24, color="#FF6B35", weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        msg_example.move_to(LEFT * 3 + UP * 0.5)

        # Highlight boxes for DE 11 and 41
        de11_box = SurroundingRectangle(msg_example[3], color="#FF6B35", buff=0.1)
        de41_box = SurroundingRectangle(msg_example[4], color="#FF6B35", buff=0.1)

        scene.play(LaggedStart(*[FadeIn(line, shift=RIGHT) for line in msg_example], lag_ratio=0.2))
        scene.play(Create(de11_box), Create(de41_box))
        scene.wait(0.5)

        # Extract key animation - arrow moved left and properly aligned
        arrow = Arrow(LEFT * 0.8 + UP * 0.2, RIGHT * 1.2 + UP * 0.2, color=YELLOW, buff=0.1, stroke_width=4)

        # Larger box to contain the full key text
        key_box = Rectangle(width=4.8, height=1, color=YELLOW, fill_opacity=0.3, stroke_width=3)
        key_box.move_to(RIGHT * 3.6 + UP * 0.2)
        key_label = Text('Key = "29110001|000001"', font_size=20, color=YELLOW, weight=BOLD, font="monospace")
        key_label.move_to(key_box.get_center())

        scene.play(Create(arrow))
        scene.play(Create(key_box), Write(key_label))
        scene.wait(1)

        # Show XML config
        xml_config = VGroup(
            Text("<key>41,11</key>", font_size=22, color=COLOR_XML, font="monospace"),
            Text("← Configurable!", font_size=18, color=GRAY, slant=ITALIC),
        ).arrange(RIGHT, buff=0.3)
        xml_config.move_to(DOWN * 1.5)

        scene.play(FadeIn(xml_config, shift=UP))
        scene.wait(2)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 4: Request Flow (25-30s)
        # =======================================================================
        flow_title = Text("Request Flow: 3 Concurrent Requests", font_size=32, weight=BOLD)
        flow_title.to_edge(UP, buff=0.3)
        scene.play(Write(flow_title), run_time=0.6)
        scene.wait(0.3)
        scene.play(flow_title.animate.scale(0.8).to_edge(UP, buff=0.1))

        # Simplified architecture for flow - all aligned vertically with bigger text
        threads_area = VGroup(*[create_thread_indicator(f"T{i+1}", "active") for i in range(3)])
        threads_area.arrange(DOWN, buff=0.7).scale(0.9)
        threads_area.move_to(LEFT * 5.5)

        qmux_comp = Rectangle(width=1.8, height=2.8, color=ORANGE, fill_opacity=0.2, stroke_width=3)
        qmux_comp.move_to(LEFT * 3)
        qmux_lbl = Text("QMUX", font_size=22, color=ORANGE, weight=BOLD)
        qmux_lbl.move_to(qmux_comp.get_top() + DOWN * 0.4)

        outq_viz = create_queue_viz("Outgoing", num_slots=3)
        outq_viz.move_to(ORIGIN)

        channel_viz = Rectangle(width=2.2, height=0.7, color=COLOR_CHANNEL, fill_opacity=0.3, stroke_width=3)
        channel_viz.move_to(RIGHT * 3)
        ch_lbl = Text("Channel", font_size=18, color=COLOR_CHANNEL, weight=BOLD)
        ch_lbl.move_to(channel_viz.get_center())

        processor_circle = Circle(radius=0.9, color="#E6CCFF", fill_opacity=0.3, stroke_width=3)
        processor_circle.move_to(RIGHT * 5.5)
        proc_lbl = Text("Processor", font_size=18, color="#E6CCFF", weight=BOLD)
        proc_lbl.move_to(processor_circle.get_center())

        scene.play(
            LaggedStart(*[FadeIn(t) for t in threads_area], lag_ratio=0.15),
            Create(qmux_comp), Write(qmux_lbl),
            FadeIn(outq_viz),
            Create(channel_viz), Write(ch_lbl),
            Create(processor_circle), Write(proc_lbl)
        )
        scene.wait(0.5)

        # Create 3 messages
        messages = []
        keys = []
        for i in range(3):
            msg = create_message_box(f"M{i+1}", "0200", "29110001", f"00000{i+1}", GREEN)
            msg.scale(0.5)
            msg.move_to(threads_area[i].get_right() + RIGHT * 0.5)
            messages.append(msg)

            key = create_key_tag(f"K{i+1}:{f'00000{i+1}'}")
            key.scale(0.6)
            keys.append(key)

        # Animate request flow
        for i, (msg, key, thread) in enumerate(zip(messages, keys, threads_area)):
            # Message appears
            scene.play(FadeIn(msg, shift=RIGHT), run_time=0.4)

            # Key extracted
            key.move_to(msg.get_top() + UP * 0.2)
            scene.play(FadeIn(key, scale=0.5), run_time=0.3)

            # Thread goes to waiting
            thread[0].set_fill(YELLOW, opacity=0.6)
            wait_icon = Text("⏱", font_size=14)
            wait_icon.next_to(thread, RIGHT, buff=0.1)
            scene.play(FadeIn(wait_icon), run_time=0.2)

            # Message to outgoing queue
            target_slot = outq_viz[1][i]
            scene.play(
                msg.animate.scale(0.8).move_to(target_slot.get_center()),
                key.animate.move_to(target_slot.get_right() + RIGHT * 0.3),
                run_time=0.6
            )
            scene.wait(0.3)

        scene.wait(1)

        # ChannelAdaptor sends them
        for i, msg in enumerate(messages):
            scene.play(
                msg.animate.move_to(channel_viz.get_center()),
                keys[i].animate.fade(0.7),
                run_time=0.5
            )
            scene.play(
                msg.animate.scale(0.6).move_to(processor_circle.get_center()),
                run_time=0.7
            )
            scene.wait(0.2)

        scene.wait(1)
        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 5: Out-of-Order Response Matching (30-35s)
        # =======================================================================
        match_title = Text("Response Matching: Out of Order!", font_size=32, weight=BOLD, color=YELLOW)
        match_title.to_edge(UP, buff=0.3)
        scene.play(Write(match_title), run_time=0.6)
        scene.wait(0.3)
        scene.play(match_title.animate.scale(0.8).to_edge(UP, buff=0.1))

        # Recreate simplified layout - matching Section 4 alignment and sizes
        threads_waiting = VGroup(*[create_thread_indicator(f"T{i+1}", "waiting") for i in range(3)])
        threads_waiting.arrange(DOWN, buff=0.7).scale(0.9)
        threads_waiting.move_to(LEFT * 5.5)

        # Show what they're waiting for - bigger labels
        wait_labels = VGroup(
            Text("K1", font_size=18, color=YELLOW, weight=BOLD),
            Text("K2", font_size=18, color=YELLOW, weight=BOLD),
            Text("K3", font_size=18, color=YELLOW, weight=BOLD),
        )
        for i, (thread, label) in enumerate(zip(threads_waiting, wait_labels)):
            label.next_to(thread, RIGHT, buff=0.3)

        qmux_matcher = Rectangle(width=2.2, height=3.2, color=ORANGE, fill_opacity=0.2, stroke_width=3)
        qmux_matcher.move_to(LEFT * 2.2)
        qmux_match_lbl = Text("QMUX\nMatcher", font_size=22, color=ORANGE, weight=BOLD)
        qmux_match_lbl.move_to(qmux_matcher.get_center())

        inq_viz = create_queue_viz("Incoming", num_slots=3, color=ORANGE)
        inq_viz.move_to(RIGHT * 1.8)

        proc_resp = Circle(radius=0.9, color="#E6CCFF", fill_opacity=0.3, stroke_width=3)
        proc_resp.move_to(RIGHT * 5.5)
        proc_resp_lbl = Text("Processor", font_size=18, color="#E6CCFF", weight=BOLD)
        proc_resp_lbl.move_to(proc_resp.get_center())

        scene.play(
            LaggedStart(*[FadeIn(t) for t in threads_waiting], lag_ratio=0.15),
            *[FadeIn(l) for l in wait_labels],
            Create(qmux_matcher), Write(qmux_match_lbl),
            FadeIn(inq_viz),
            Create(proc_resp), Write(proc_resp_lbl)
        )
        scene.wait(0.5)

        # Responses arrive out of order: R3, R1, R2
        response_order = [
            (2, "R3", "0210", "K3:000003", BLUE),  # R3 first
            (0, "R1", "0210", "K1:000001", BLUE),  # R1 second
            (1, "R2", "0210", "K2:000002", BLUE),  # R2 third
        ]

        for thread_idx, resp_label, mti, key_str, color in response_order:
            # Response comes from processor
            resp_msg = create_message_box(resp_label, mti, "29110001", key_str.split(':')[1], color)
            resp_msg.scale(0.4).move_to(proc_resp.get_center())

            resp_key = create_key_tag(key_str, "#FFD700")
            resp_key.scale(0.5).move_to(resp_msg.get_top() + UP * 0.15)

            scene.play(FadeIn(resp_msg, scale=0.5), FadeIn(resp_key), run_time=0.4)
            scene.wait(0.3)

            # Move to incoming queue
            scene.play(
                resp_msg.animate.move_to(inq_viz[1][0].get_center()),
                resp_key.animate.move_to(inq_viz[1][0].get_right() + RIGHT * 0.2),
                run_time=0.6
            )
            scene.wait(0.3)

            # QMUX extracts key and matches
            flash_box = SurroundingRectangle(qmux_matcher, color=YELLOW, buff=0.05)
            scene.play(Create(flash_box), run_time=0.2)
            scene.play(FadeOut(flash_box), run_time=0.2)

            # Show matching logic - bigger text
            match_text = Text(f"Match: {key_str} → T{thread_idx+1}", font_size=18, color=GREEN, weight=BOLD)
            match_text.move_to(qmux_matcher.get_bottom() + DOWN * 0.4)
            scene.play(FadeIn(match_text, shift=UP), run_time=0.4)

            # Deliver to correct thread
            target_thread = threads_waiting[thread_idx]
            scene.play(
                resp_msg.animate.move_to(target_thread.get_left() + LEFT * 0.5),
                resp_key.animate.fade(1),
                run_time=0.8
            )

            # Thread completes
            target_thread[0].set_fill(GREEN, opacity=0.8)
            check_mark = Text("✓", font_size=24, color=GREEN, weight=BOLD)
            check_mark.move_to(target_thread.get_right() + RIGHT * 0.3)
            scene.play(
                FadeIn(check_mark, scale=2),
                FadeOut(wait_labels[thread_idx]),
                FadeOut(match_text),
                run_time=0.5
            )
            scene.wait(0.5)

        scene.wait(2)
        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 6: Edge Cases (15-20s)
        # =======================================================================
        edge_title = Text("Edge Cases", font_size=36, weight=BOLD)
        edge_title.to_edge(UP, buff=0.4)
        scene.play(Write(edge_title), run_time=0.6)
        scene.wait(0.2)

        # Split screen for two cases
        divider2 = Line(UP * 3, DOWN * 3, color=GRAY)
        scene.play(Create(divider2))

        # LEFT: Timeout - 50% bigger
        timeout_label = Text("Case 1: Timeout", font_size=32, weight=BOLD, color=RED)
        timeout_label.move_to(LEFT * 3.5 + UP * 2.2)
        scene.play(Write(timeout_label))

        t4 = create_thread_indicator("T4", "waiting")
        t4.scale(1.5).move_to(LEFT * 3.5 + UP * 0.8)
        m4 = create_message_box("M4", "0200", "29110001", "000004", GREEN)
        m4.scale(0.9).move_to(LEFT * 3.5 + UP * 0.1)

        clock = Text("⏰", font_size=60)
        clock.move_to(LEFT * 3.5 + DOWN * 0.7)
        timer_text = Text("30s...", font_size=30, color=YELLOW, weight=BOLD)
        timer_text.next_to(clock, DOWN, buff=0.2)

        scene.play(FadeIn(t4), FadeIn(m4))
        scene.play(FadeIn(clock), Write(timer_text))

        # Count down - bigger font
        for t in [20, 10, 5, 0]:
            new_timer = Text(f"{t}s...", font_size=30, color=YELLOW if t > 0 else RED, weight=BOLD)
            new_timer.move_to(timer_text.get_center())
            scene.play(Transform(timer_text, new_timer), run_time=0.4)

        # Returns null - bigger
        null_text = Text("returns null", font_size=30, color=RED, slant=ITALIC, weight=BOLD)
        null_text.move_to(LEFT * 3.5 + DOWN * 1.8)
        scene.play(FadeIn(null_text, shift=UP))

        code_snippet = VGroup(
            Text("if (response == null) {", font_size=16, font="monospace"),
            Text("  // Timeout!", font_size=16, font="monospace", color=RED),
            Text("  // Retry or reverse", font_size=16, font="monospace", color=GRAY),
            Text("}", font_size=16, font="monospace"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        code_snippet.move_to(LEFT * 3.5 + DOWN * 2.7)
        scene.play(FadeIn(code_snippet, shift=UP), run_time=0.6)

        # RIGHT: Unmatched response - 50% bigger
        unmatched_label = Text("Case 2: Unmatched", font_size=32, weight=BOLD, color=ORANGE)
        unmatched_label.move_to(RIGHT * 3.5 + UP * 2.2)
        scene.play(Write(unmatched_label))

        orphan_resp = create_message_box("R99", "0210", "29110001", "000099", BLUE)
        orphan_resp.scale(0.9).move_to(RIGHT * 3.5 + UP * 0.6)
        orphan_key = create_key_tag("K99:000099")
        orphan_key.scale(1.1).move_to(orphan_resp.get_top() + UP * 0.25)

        scene.play(FadeIn(orphan_resp), FadeIn(orphan_key))

        question = Text("No matching request!", font_size=27, color=ORANGE, slant=ITALIC, weight=BOLD)
        question.move_to(RIGHT * 3.5 + DOWN * 0.3)
        scene.play(FadeIn(question, shift=UP))
        scene.wait(0.5)

        # Arrow pointing down - thicker
        down_arrow = Arrow(RIGHT * 3.5 + DOWN * 0.65, RIGHT * 3.5 + DOWN * 1.15, color=ORANGE, stroke_width=6)
        scene.play(Create(down_arrow))

        unhandled_box = Rectangle(width=3.75, height=0.9, color=ORANGE, fill_opacity=0.3, stroke_width=3)
        unhandled_box.move_to(RIGHT * 3.5 + DOWN * 1.5)
        unhandled_lbl = Text("Unhandled Queue", font_size=21, color=ORANGE, weight=BOLD)
        unhandled_lbl.move_to(unhandled_box.get_center())

        scene.play(Create(unhandled_box), Write(unhandled_lbl))

        or_text = Text("or", font_size=21, color=GRAY, slant=ITALIC)
        or_text.move_to(RIGHT * 3.5 + DOWN * 2.15)
        scene.play(FadeIn(or_text))

        listener_box = Rectangle(width=4.2, height=0.9, color=ORANGE, fill_opacity=0.3, stroke_width=3)
        listener_box.move_to(RIGHT * 3.5 + DOWN * 2.7)
        listener_lbl = Text("ISORequestListener", font_size=21, color=ORANGE, font="monospace", weight=BOLD)
        listener_lbl.move_to(listener_box.get_center())
        scene.play(Create(listener_box), Write(listener_lbl))

        scene.wait(2.5)
        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 6.5: ChannelAdaptor Configuration (12-15s)
        # =======================================================================
        channel_config_title = Text("ChannelAdaptor Configuration", font_size=36, weight=BOLD)
        channel_config_title.to_edge(UP, buff=0.3)
        scene.play(Write(channel_config_title), run_time=0.6)
        scene.wait(0.2)
        scene.play(channel_config_title.animate.scale(0.75).to_edge(UP, buff=0.15))

        # Create ChannelAdaptor XML configuration
        channel_code_str = """<channel-adaptor name="my-channel">
  <channel class="...NACChannel"
           packager="...GenericPackager">
    <property name="host" value="localhost" />
    <property name="port" value="8000" />
    <property name="timeout" value="300000" />
  </channel>
  <in>send</in>
  <out>receive</out>
  <reconnect-delay>10000</reconnect-delay>
</channel-adaptor>"""

        # Create the Code mobject
        channel_code_block = Code(
            code_string=channel_code_str,
            language="xml",
            formatter_style="native",
            add_line_numbers=False,
            background="rectangle",
            paragraph_config={
                "font": "monospace",
                "font_size": 24,
                "line_spacing": 1
            }
        )

        # Extract the Paragraph (text lines) from the Code mobject
        channel_xml_lines = channel_code_block[1]

        # Set colors for specific lines
        channel_xml_lines[1].set_color(BLUE)  # Channel type
        channel_xml_lines[3].set_color(COLOR_CHANNEL)  # host
        channel_xml_lines[4].set_color(COLOR_CHANNEL)  # port
        channel_xml_lines[5].set_color(COLOR_CHANNEL)  # timeout
        channel_xml_lines[7].set_color(ORANGE)  # in (outgoing)
        channel_xml_lines[8].set_color(ORANGE)  # out (incoming)
        channel_xml_lines[9].set_color(GREEN)  # reconnect-delay

        # Position the text block
        channel_xml_lines.move_to(LEFT * 2.5 + DOWN * 0.2)

        # Define annotation parameters
        CHANNEL_ANNOTATION_FONT_SIZE = 24
        CHANNEL_ANNOTATION_COLOR = WHITE

        # Create annotations for ChannelAdaptor
        channel_annotations = VGroup(
            Text("← Channel type", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
            Text("← Server address", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
            Text("← Server port", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
            Text("← Socket timeout", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
            Text("← Outgoing queue", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
            Text("← Incoming queue", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
            Text("← Reconnect delay", font_size=CHANNEL_ANNOTATION_FONT_SIZE, color=CHANNEL_ANNOTATION_COLOR, slant=ITALIC),
        )

        CHANNEL_ANNOTATION_BUFFER = 1.5

        # Position annotations relative to code lines using the same technique as QMUX
        channel_code_right_x = channel_xml_lines.get_right()[0]
        channel_annotation_column_x = channel_code_right_x + CHANNEL_ANNOTATION_BUFFER

        # Map annotations to their corresponding lines
        channel_code_lines = [
            channel_xml_lines[1],  # channel type
            channel_xml_lines[3],  # host
            channel_xml_lines[4],  # port
            channel_xml_lines[5],  # timeout
            channel_xml_lines[7],  # in
            channel_xml_lines[8],  # out
            channel_xml_lines[9],  # reconnect-delay
        ]

        for ann, code_line in zip(channel_annotations, channel_code_lines):
            ann.set_x(channel_annotation_column_x, direction=LEFT)
            ann.match_y(code_line)

        # Animation
        scene.play(
            FadeIn(channel_xml_lines, shift=RIGHT, lag_ratio=0.1),
            run_time=3
        )
        scene.wait(0.5)
        scene.play(LaggedStart(*[FadeIn(ann, shift=LEFT) for ann in channel_annotations], lag_ratio=0.15), run_time=2)
        scene.wait(2)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

        # =======================================================================
        # SECTION 7: QMUX Configuration (12-15s)
        # =======================================================================
        xml_title = Text("QMUX Configuration", font_size=36, weight=BOLD)
        xml_title.to_edge(UP, buff=0.3)
        scene.play(Write(xml_title), run_time=0.6)
        scene.wait(0.2)
        scene.play(xml_title.animate.scale(0.75).to_edge(UP, buff=0.15))

        # Create a single triple-quoted string
        code_str = """<mux class="...QMUX" name="mymux">
  <key>41,11</key>
  <in>receive</in>
  <out>send</out>
  <ready>...channel-ready</ready>
  <unhandled>orphans</unhandled>
  <request-listener .../>
</mux>"""  # <-- Note: The </mux> is NOT indented here in the string.

        # 1. Create the Code mobject TEMPORARILY
        code_block = Code(
            code_string=code_str,
            language="xml",
            formatter_style="native",
            add_line_numbers=False,
            background="rectangle",
            paragraph_config={
                "font": "monospace",
                "font_size": 24,
                "line_spacing": 1
            }
        )

        # Extract ONLY the text (the Paragraph mobject)
        xml_lines = code_block[1]

        xml_lines[0].set_color(COLOR_XML)
        xml_lines[1].set_color(YELLOW)
        xml_lines[2].set_color(COLOR_CHANNEL)
        xml_lines[3].set_color(COLOR_CHANNEL)
        xml_lines[4].set_color(GREEN)
        xml_lines[5].set_color(ORANGE)
        xml_lines[6].set_color(GRAY)
        xml_lines[7].set_color(COLOR_XML)

        # Move the text block
        xml_lines.move_to(LEFT * 3.5 + DOWN * 0.2)

        # 2. Annotations
        # --- THIS IS THE FIX FOR FONT AND ALIGNMENT ---
        # Use a brighter color and larger font size for clarity
        ANNOTATION_FONT_SIZE = 24  # Increased font size
        ANNOTATION_COLOR = WHITE  # Changed from GRAY to WHITE for better visibility

        annotations = VGroup(
            Text("← Correlation fields", font_size=ANNOTATION_FONT_SIZE, color=ANNOTATION_COLOR, slant=ITALIC),
            Text("← Incoming queue", font_size=ANNOTATION_FONT_SIZE, color=ANNOTATION_COLOR, slant=ITALIC),
            Text("← Outgoing queue", font_size=ANNOTATION_FONT_SIZE, color=ANNOTATION_COLOR, slant=ITALIC),
            Text("← Channel ready flag", font_size=ANNOTATION_FONT_SIZE, color=ANNOTATION_COLOR, slant=ITALIC),
            Text("← Unmatched messages", font_size=ANNOTATION_FONT_SIZE, color=ANNOTATION_COLOR, slant=ITALIC),
            Text("← Optional handler", font_size=ANNOTATION_FONT_SIZE, color=ANNOTATION_COLOR, slant=ITALIC),
        )

        ANNOTATION_BUFFER = 1.5

        # Position annotations relative to the text lines
        # We now specify aligned_edge=LEFT to force the left edges to align

        code_right_x = xml_lines.get_right()[0]
        annotation_column_x = code_right_x + ANNOTATION_BUFFER

        for ann, code_line in zip(annotations, xml_lines[1:7]):
            ann.set_x(annotation_column_x, direction=LEFT)
            ann.match_y(code_line)

        # --- END FIX ---

        # 3. Animation
        scene.play(
            FadeIn(xml_lines, shift=RIGHT, lag_ratio=0.1),
            run_time=3
        )
        scene.wait(0.5)

        scene.play(
            FadeIn(annotations, shift=LEFT, lag_ratio=0.15),
            run_time=5
        )
        scene.wait(2)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])


        # =======================================================================
        # SECTION 8: Summary (10-12s)
        # =======================================================================
        summary_title = Text("QMUX Benefits", font_size=40, weight=BOLD)
        summary_title.to_edge(UP, buff=0.5)
        scene.play(Write(summary_title), run_time=0.6)
        scene.wait(0.3)

        benefits = VGroup(
            Text("✓ Multiple concurrent requests on single channel", font_size=24, color=GREEN),
            Text("✓ Automatic response correlation by key", font_size=24, color=GREEN),
            Text("✓ Out-of-order handling", font_size=24, color=GREEN),
            Text("✓ Timeout protection", font_size=24, color=GREEN),
            Text("✓ Configurable correlation fields", font_size=24, color=GREEN),
            Text("✓ Production-grade reliability", font_size=24, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        benefits.move_to(DOWN * 0.3)

        scene.play(LaggedStart(*[FadeIn(benefit, shift=RIGHT) for benefit in benefits], lag_ratio=0.3), run_time=3)
        scene.wait(2.5)

        scene.play(*[FadeOut(mob) for mob in scene.mobjects])

    @staticmethod
    def construct_putting_together(scene):
        """Putting it together (10-15s)."""
        # Title
        title = Text("jPOS Stack in Action", font_size=40, weight=BOLD)
        title.to_edge(UP)
        scene.play(Write(title), run_time=0.8)

        # Flow 1 - Sending
        flow1_label = Text("Sending:", font_size=28, weight=BOLD)
        flow1_label.move_to(UP * 1.8 + LEFT * 3)

        flow1_blocks = VGroup(
            Text("ISOMsg", font_size=22, color=COLOR_ISOMSG),
            Text("→", font_size=24),
            Text("Packager", font_size=22, color=COLOR_PACKAGER),
            Text("→", font_size=24),
            Text("Bytes", font_size=22, color=GREEN),
            Text("→", font_size=24),
            Text("Channel", font_size=22, color=COLOR_CHANNEL),
            Text("→", font_size=24),
            Text("Socket", font_size=22, color=BLUE),
        ).arrange(RIGHT, buff=0.2)
        flow1_blocks.next_to(flow1_label, DOWN, buff=0.4)

        scene.play(Write(flow1_label))
        scene.play(LaggedStart(*[FadeIn(block, shift=RIGHT) for block in flow1_blocks], lag_ratio=0.1))
        scene.wait(1)

        # Flow 2 - QMUX Request/Response
        flow2_label = Text("QMUX Request/Response:", font_size=28, weight=BOLD)
        flow2_label.move_to(DOWN * 0.5 + LEFT * 3)

        flow2_blocks = VGroup(
            Text("ISOMsg", font_size=22, color=COLOR_ISOMSG),
            Text("→", font_size=24),
            Text("QMUX", font_size=22, color=COLOR_QMUX),
            Text("→", font_size=24),
            Text("Queue", font_size=22, color=COLOR_QMUX),
            Text("→", font_size=24),
            Text("Channel", font_size=22, color=COLOR_CHANNEL),
            Text("→", font_size=24),
            Text("Response", font_size=22, color=BLUE),
            Text("→", font_size=24),
            Text("Key Match", font_size=22, color=YELLOW),
            Text("→", font_size=24),
            Text("Deliver", font_size=22, color=GREEN),
        ).arrange(RIGHT, buff=0.2)
        flow2_blocks.scale(0.85)
        flow2_blocks.next_to(flow2_label, DOWN, buff=0.4)

        scene.play(Write(flow2_label))
        scene.play(LaggedStart(*[FadeIn(block, shift=RIGHT) for block in flow2_blocks], lag_ratio=0.08))
        scene.wait(1.5)

        # Final overlay
        final_text = Text("Production-grade ISO 8583 toolkit", font_size=32, color=COLOR_JPOS_BRAND, weight=BOLD)
        final_text.to_edge(DOWN, buff=1)
        scene.play(FadeIn(final_text, shift=UP))
        scene.wait(2)
        scene.play(*[FadeOut(mob) for mob in scene.mobjects])


# =============================================================================
# INDIVIDUAL SCENE CLASSES
# =============================================================================

class ColdOpen(Scene):
    """Cold open with title card (2-3s)."""
    def construct(self):
        ISO8583Scenes.construct_cold_open(self)


class WhatIsISO8583(Scene):
    """Introduction to ISO 8583 (10-15s)."""
    def construct(self):
        ISO8583Scenes.construct_what_is_iso8583(self)


class MeetTheMessage(Scene):
    """Display the full message structure (15-20s)."""
    def construct(self):
        ISO8583Scenes.construct_meet_the_message(self)


class MTIDeepDive(Scene):
    """MTI breakdown (20-30s)."""
    def construct(self):
        ISO8583Scenes.construct_mti_deep_dive(self)


class BitmapConcept(Scene):
    """Bitmap explanation with bit numbering (25-35s)."""
    def construct(self):
        ISO8583Scenes.construct_bitmap_concept(self)


class SecondaryBitmap(Scene):
    """Secondary bitmap explanation (8-12s)."""
    def construct(self):
        ISO8583Scenes.construct_secondary_bitmap(self)


class DataElementsFixedVsVariable(Scene):
    """Compare fixed and variable length fields (35-45s)."""
    def construct(self):
        ISO8583Scenes.construct_data_elements_fixed_vs_variable(self)


class AnotherFixedExample(Scene):
    """Show DE 11 STAN (10-12s)."""
    def construct(self):
        ISO8583Scenes.construct_another_fixed_example(self)


class DataTypesCheatSheet(Scene):
    """Data types reference (10-15s)."""
    def construct(self):
        ISO8583Scenes.construct_data_types_cheat_sheet(self)


class OnTheWire(Scene):
    """Network transmission visualization (20-30s)."""
    def construct(self):
        ISO8583Scenes.construct_on_the_wire(self)


class RecapAndPointers(Scene):
    """Final summary (10-15s)."""
    def construct(self):
        ISO8583Scenes.construct_recap_and_pointers(self)


# =============================================================================
# jPOS SCENE CLASSES
# =============================================================================

class JPOSIntro(Scene):
    """Intro to jPOS (8-12s)."""
    def construct(self):
        JPOSScenes.construct_jpos_intro(self)


class ISOMsgComposite(Scene):
    """ISOMsg uses Composite pattern (20-25s)."""
    def construct(self):
        JPOSScenes.construct_isomsg_composite(self)


class PackagerConcept(Scene):
    """What is a Packager? (25-30s)."""
    def construct(self):
        JPOSScenes.construct_packager_concept(self)


class PackagerDefinition(Scene):
    """Defining a Packager (15-20s)."""
    def construct(self):
        JPOSScenes.construct_packager_definition(self)


class CompositeSubfields(Scene):
    """Composite subfields - DE 3 (25-35s)."""
    def construct(self):
        JPOSScenes.construct_composite_subfields(self)


class BytePacking(Scene):
    """Byte-by-byte packing vignette (30-40s)."""
    def construct(self):
        JPOSScenes.construct_byte_packing(self)


class Channels(Scene):
    """Channels (20-25s)."""
    def construct(self):
        JPOSScenes.construct_channels(self)


class QMUX(Scene):
    """QMUX - Multiplexing (35-45s)."""
    def construct(self):
        JPOSScenes.construct_qmux(self)


class PuttingTogether(Scene):
    """Putting it together (10-15s)."""
    def construct(self):
        JPOSScenes.construct_putting_together(self)


# =============================================================================
# FULL PRESENTATION (All scenes chained)
# =============================================================================

class FullPresentation(Scene):
    """Complete presentation with all scenes chained together."""

    def construct(self):
        # Scene 0: Cold Open
        ISO8583Scenes.construct_cold_open(self)

        # Scene 1: What is ISO 8583?
        ISO8583Scenes.construct_what_is_iso8583(self)

        # Scene 2: Meet the Message
        ISO8583Scenes.construct_meet_the_message(self)

        # Scene 3: MTI Deep Dive
        ISO8583Scenes.construct_mti_deep_dive(self)

        # Scene 4: Bitmap Concept
        ISO8583Scenes.construct_bitmap_concept(self)

        # Scene 5: Secondary Bitmap
        ISO8583Scenes.construct_secondary_bitmap(self)

        # Scene 6: Data Elements Fixed vs Variable
        ISO8583Scenes.construct_data_elements_fixed_vs_variable(self)

        # Scene 7: Another Fixed Example (DE 11)
        ISO8583Scenes.construct_another_fixed_example(self)

        # Scene 8: Data Types Cheat Sheet
        ISO8583Scenes.construct_data_types_cheat_sheet(self)

        # Scene 9: On the Wire
        ISO8583Scenes.construct_on_the_wire(self)

        # Scene 10: Recap and Pointers
        ISO8583Scenes.construct_recap_and_pointers(self)


class FullPresentationWithJPOS(Scene):
    """Complete presentation with ISO 8583 and jPOS scenes chained together."""

    def construct(self):
        # ===== ISO 8583 Scenes =====
        # Scene 0: Cold Open
        ISO8583Scenes.construct_cold_open(self)

        # Scene 1: What is ISO 8583?
        ISO8583Scenes.construct_what_is_iso8583(self)

        # Scene 2: Meet the Message
        ISO8583Scenes.construct_meet_the_message(self)

        # Scene 3: MTI Deep Dive
        ISO8583Scenes.construct_mti_deep_dive(self)

        # Scene 4: Bitmap Concept
        ISO8583Scenes.construct_bitmap_concept(self)

        # Scene 5: Secondary Bitmap
        ISO8583Scenes.construct_secondary_bitmap(self)

        # Scene 6: Data Elements Fixed vs Variable
        ISO8583Scenes.construct_data_elements_fixed_vs_variable(self)

        # Scene 7: Another Fixed Example (DE 11)
        ISO8583Scenes.construct_another_fixed_example(self)

        # Scene 8: Data Types Cheat Sheet
        ISO8583Scenes.construct_data_types_cheat_sheet(self)

        # Scene 9: On the Wire
        ISO8583Scenes.construct_on_the_wire(self)

        # Scene 10: Recap and Pointers
        ISO8583Scenes.construct_recap_and_pointers(self)

        # ===== jPOS Scenes =====
        # Scene J0: jPOS Intro
        JPOSScenes.construct_jpos_intro(self)

        # Scene J1: ISOMsg Composite Pattern
        JPOSScenes.construct_isomsg_composite(self)

        # Scene J2: Packager Definition (show XML config first)
        JPOSScenes.construct_packager_definition(self)

        # Scene J3: Packager Concept (then show it in action)
        JPOSScenes.construct_packager_concept(self)

        # Scene J4: Composite Subfields
        JPOSScenes.construct_composite_subfields(self)

        # Scene J5: Byte Packing
        JPOSScenes.construct_byte_packing(self)

        # Scene J6: Channels
        JPOSScenes.construct_channels(self)

        # Scene J7: QMUX
        JPOSScenes.construct_qmux(self)

        # Scene J8: Putting Together
        JPOSScenes.construct_putting_together(self)
