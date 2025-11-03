# ISO 8583 Message Format — Manim Animation Script (Packed BCD Encoding, No Code)

> **Correction note:** The previous draft showed all numeric fields in ASCII for readability. In many real stacks (including your examples), **numeric fields are encoded in packed BCD (2 digits per byte)** and **LLVAR lengths are 1 byte in BCD** (e.g., PAN length `0x16` for 16 digits). This version updates the examples accordingly.


**Purpose:** A clear, fast-paced animation that introduces ISO 8583, shows how a message is structured (MTI, bitmaps, data elements), and explains how messages travel over sockets with a length prefix.  
**Audience:** Engineers/product folks new to card networks, gateways, or POS/host integrations.  
**Length target:** ~4–6 minutes.

---

## Learning objectives

By the end, the viewer will be able to:

1. Recognize the **MTI**, **Primary/Secondary Bitmaps**, and **Data Elements (DEs)** in a message dump.
2. Understand how the **bitmap** signals which **DEs** are present.
3. Distinguish **fixed** vs **variable-length** fields and common data types.
4. Understand why a **length prefix** is added for transmission over sockets.

---

## Visual system & tone

- **Style:** Clean, minimal, high-contrast. Dark background with bright accent colors for highlights.
- **Color cues:**  
  - MTI: cyan  
  - Bitmaps: orange (primary) / amber (secondary)  
  - Data elements: green  
  - Length prefix (network): purple
- **Motion:** Subtle zooms, fades, and slide-ins. Use braces/underlines, focus boxes, and binary “flip” reveals for mapping bits → fields.
- **On-screen text:** Short, declarative captions; keep paragraphs in the voiceover.

---

## Encoding profile used in this script

- **MTI:** ASCII digits (`'0200' → 0x30 0x32 0x30 0x30`). *(Many hosts also use BCD `0x02 0x00`; see appendix.)*
- **Bitmaps:** 8 bytes **binary** each (primary + secondary when bit 1 is set).  
- **Numeric DEs (e.g., 2, 4, 7):** **Packed BCD** (two digits per byte).  
- **LLVAR length (for DE 2):** **1 byte BCD** (e.g., PAN length 16 → `0x16`).  
- **Examples below:** `DE 2` (PAN, LLVAR), `DE 4` (Amount, N12), `DE 7` (Transmission date & time, N10).

> If you prefer a “readability mode” for the video overlays, keep the **visual labels** as decimal/ASCII strings, but drive the **raw bytes** using the packed BCD shown here.

---

## Canonical example payload (for the visuals)

> This is **for display only**; no parsing code here—just the bytes you will **draw** and **highlight**.

### Human-readable segmentation (with raw bytes)

- **MTI** (ASCII): `0200`  
  - **Bytes:** `30 32 30 30`
- **Primary bitmap** (8 bytes): `D2 00 00 00 00 00 00 00`  
  - First byte `D2` = `11010010₂` ⇒ bits set **1**, **2**, **4**, **7**  
  - Meaning: **bit 1** = secondary bitmap present; **DE 2**, **DE 4**, **DE 7** are present
- **Secondary bitmap** (8 bytes): `00 00 00 00 00 00 00 00` (required since bit 1 = 1)
- **DE 2** (PAN, **LLVAR** packed BCD): length **1 byte BCD** + value  
  - PAN length: **16** → **`0x16`**  
  - PAN (16 digits): `4539681234567890` → **`45 39 68 12 34 56 78 90`** (8 bytes)
- **DE 4** (Amount, **N12 packed BCD**): `000000001000` → **`00 00 00 00 10 00`** (6 bytes)
- **DE 7** (Transmission date & time, **N10 packed BCD**): `1013123039` (MMDDhhmmss) → **`10 13 12 30 39`** (5 bytes)

### Entire message (no network length prefix)

- **Total length:** **40 bytes**  
- **Hex (continuous):**  
  `30 32 30 30 D2 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 45 39 68 12 34 56 78 90 00 00 00 00 10 00 10 13 12 30 39`

### Length prefix for sockets (added later in the animation)

- **2-byte big-endian length header** (not including the header itself): **`00 28`** (40 bytes)  
- Transmission frame (for the final scene):  
  `00 28 | 30 32 30 30 | D2 00 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00 | 16 | 45 39 68 12 34 56 78 90 | 00 00 00 00 10 00 | 10 13 12 30 39`

---

## Script & storyboard (scene by scene)

### 0) Cold open (2–3 s)
- **Visual:** Title card slides in: “**ISO 8583 in 5 Minutes**”. Subline: “Messages behind card payments.”
- **VO:** “ISO 8583 is an old, battle-tested standard that still powers card payments today. In a few minutes, let’s read one message together.”

---

### 1) What is ISO 8583? (10–15 s)
- **Visual:** Standard name appears; quick timeline marker “1987 → today”.
- **On-screen text:** “**Goal:** Understand the message format.”
- **VO:** “ISO 8583 defines how payment systems talk—authorization, financial transactions, reversals, network management—using a compact message layout.”

---

### 2) Meet the message (15–20 s)
- **Visual:** A horizontal “packet strip” fades in, left-to-right blocks labeled:
  - `MTI` | `Primary Bitmap` | `Secondary Bitmap` | `DE 2` | `DE 4` | `DE 7`
- The **raw bytes** for each segment appear beneath each block (per the BCD profile above).
- **VO:** “A message has a Message Type Identifier, one or two bitmaps indicating which fields are present, and then the data elements themselves.”

---

### 3) MTI deep dive (20–30 s)
- **Visual:** MTI block **zooms**, others **dim**. MTI bytes `30 32 30 30` with ASCII overlay `0 2 0 0`.  
- Show a simple MTI breakdown:
  - **0**: ISO version (legacy)
  - **2**: Class = financial
  - **0**: Function = request
  - **0**: Origin = acquirer
- **On-screen text bullets (brief):**
  - `0100/0110` = authorization request/response
  - `0200/0210` = financial request/response
  - `0800/0810` = network management request/response
- **VO:** “`0200` is a financial request. Pair it with `0210` for the response. You’ll also see `0100/0110` for authorization and `0800/0810` for network messages.”

> **Note:** If your stack uses **BCD MTI** (`0x02 0x00`), you can still show the overlay “0200” while keeping the raw bytes as two packed BCD bytes.

---

### 4) Bitmap concept (25–35 s)
- **Visual:** Primary bitmap block **highlights**. Show bytes: `D2 00 00 00 00 00 00 00`.
- Animate the **first byte** expanding to a binary row: `11010010`. Add a **bit index ruler** `1 … 8` left-to-right (bit **1** at the leftmost).
- **Callouts:**
  - **Bit 1 = 1** → “**Secondary bitmap present**”
  - **Bit 2 = 1** → “DE **2** present”
  - **Bit 4 = 1** → “DE **4** present”
  - **Bit 7 = 1** → “DE **7** present”
- **VO:** “Each bit says whether a data element is present. Here, bit 1 means we have a secondary bitmap. Bits 2, 4, and 7 say: include DE 2, DE 4, and DE 7.”

---

### 5) Show the secondary bitmap (8–12 s)
- **Visual:** Secondary bitmap block lights up: `00 00 00 00 00 00 00 00`.  
- **Caption:** “Secondary bitmap extends fields up to **DE 128**.”
- **VO:** “Even if the secondary bitmap is all zeros, it must appear when bit 1 is set—making room for fields 65–128.”

---

### 6) Data Elements — fixed vs variable (35–45 s)
- **Visual:** Bring **DE 2** and **DE 4** to the foreground side-by-side.
- **DE 2 (LLVAR packed) animation:**
  - Brace around **`0x16`** with label “**length = 16 digits (1 byte BCD)**”.
  - Then highlight `45 39 68 12 34 56 78 90` as the **value** (with an overlay “4539681234567890”).
  - Caption: “**DE 2 — PAN (LLVAR, packed BCD)**”.
- **DE 4 (fixed N12 packed) animation:**
  - Brace the six bytes `00 00 00 00 10 00` with label “**N12 = 6 bytes (packed)**”.
  - Caption: “**DE 4 — Amount (N 12, packed BCD)**”.
- **VO:** “Variable-length numeric fields prefix their digit count in BCD; fixed numeric fields are packed—two digits per byte.”

---

### 7) Another fixed example (10–12 s)
- **Visual:** Highlight **DE 7**: bytes `10 13 12 30 39` with annotation “**MMDDhhmmss (N10 packed)**” and overlay “1013123039”.
- **Caption:** “**DE 7 — Transmission date & time (N 10, packed BCD)**”.
- **VO:** “DE 7 is a timestamp—month, day, hour, minute, second—useful for clocks and reconciliation.”

---

### 8) Data types cheat-sheet (10–15 s)
- **Visual:** Compact grid of tags with micro-examples:
  - **N (packed BCD)**, **AN** (alphanumeric), **ANS** (printable), **B** (binary), **Z** (track data), **LLVAR/LLLVAR** (variable).
- **VO:** “You’ll meet numeric, alphanumeric, printable, and binary fields. Track data and variable-length types are common in POS flows.”

---

### 9) On the wire — length prefix & sockets (20–30 s)
- **Visual:** The original message collapses into a compact block. A **purple** 2-byte header appears to its **left**: `00 28`.  
  - Label: “**2-byte big-endian length (40)** (header not included) ”.
- Cut to a **network line**: POS/Client → **Socket** → Host.  
- The frame `00 28 | …message…` travels across.
- **VO:** “Over TCP sockets, messages are framed with a length header—here, `00 28` for 40 bytes. Some stacks add ISO headers or use 4 bytes, but the idea is the same: frame, send, parse.”

---

### 10) Recap & pointers (10–15 s)
- **Visual:** Quick checklist ticks:
  - MTI classifies the message
  - Bitmap lists present fields
  - Fixed vs variable elements (packed BCD)
  - Length prefix for transport
- **VO:** “Now you can read an ISO 8583 at a glance. MTI tells you the intent; bitmaps tell you which fields are here; and a tiny length header keeps it moving across the wire.”

---

## Optional appendices

### A) Alternative MTI encoding (packed BCD)
- **MTI** `0200` as **BCD**: `02 00` (2 bytes), not ASCII `30 32 30 30`.  
- Recalculate the total length accordingly: **38 bytes** (2 + 8 + 8 + 1 + 8 + 6 + 5).  
- **Length prefix (2-byte BE)**: `00 26` (decimal 38).

### B) “Readability mode” (ASCII digits for demos)
If you decide to present everything in ASCII for teaching, the message becomes longer:
- **DE 2 length** is `31 36` (“16”), **PAN** is 16 ASCII bytes, **DE 4** is 12 ASCII bytes, **DE 7** is 10 ASCII bytes.  
- Total rises to **~60 bytes**; a 2-byte BE length would be `00 3C`.  
- Keep a caption warning: “**ASCII for display; real systems often use packed BCD**.”

### C) Common DEs to recognize quickly
`3` Processing Code, `7` Transmission Date/Time, `11` STAN, `12/13` Local Time/Date, `37` RRN, `39` Response Code, `41/42` Terminal/Merchant IDs.

### D) Encoding caveats
Real deployments may use **BCD**, **ASCII**, or **EBCDIC**; **packed** numeric fields; and **ISO headers** (e.g., TPDU) ahead of the MTI/bitmap. Always align the animation with the target host’s dialect.

---

## On-screen text (exact strings to display)

- “ISO 8583 — Still powering card payments”
- “Goal: Understand the message format”
- “MTI = 0200 (Financial Request)”
- “Primary Bitmap (8 bytes)”
- “Bit 1 = Secondary bitmap present”
- “DE 2 present” / “DE 4 present” / “DE 7 present”
- “Secondary Bitmap (fields 65–128)”
- “DE 2 — PAN (LLVAR, packed BCD): 0x16 + value”
- “DE 4 — Amount (N 12, packed BCD)”
- “DE 7 — Transmission date & time (N 10, packed BCD)”
- “On the wire: 2-byte length prefix (big-endian)”
- “Recap: MTI • Bitmap • Data Elements • Length Prefix”

---

## Timing guide (approx.)

- Cold open & intro: **0:15**
- Message structure overview: **0:20**
- MTI deep dive: **0:25**
- Bitmap explanation: **0:35**
- DEs (fixed/variable + examples): **0:45**
- Datatypes cheat-sheet: **0:15**
- Network framing & sockets: **0:25**
- Recap: **0:15**  
**Total:** ~**3:15–3:45** (room to breathe to ~5:00 with pauses)

---

## Ready-to-draw byte cheat sheet

- **MTI (ASCII)**: `30 32 30 30` (overlay “0200”)  
- **Primary bitmap**: `D2 00 00 00 00 00 00 00`  
- **Secondary bitmap**: `00 00 00 00 00 00 00 00`  
- **DE 2 (LLVAR packed BCD)**: length **`16 → 0x16`**, value **`45 39 68 12 34 56 78 90`**  
- **DE 4 (N12 packed BCD)**: `00 00 00 00 10 00`  
- **DE 7 (N10 packed BCD)**: `10 13 12 30 39`  
- **2-byte length (BE)**: `00 28` (prepend for the socket scene)
