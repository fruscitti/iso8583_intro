# ISO 8583 Message Format — Manim Animation Script (No Code)

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

## Assumptions for the example message

- Dialect: **ISO 8583:1987/1993 style** (general concepts; not vendor-specific).
- Encodings in this demo:
  - **MTI & numeric DEs** shown as **ASCII digits** for readability.
  - **Bitmaps** shown as **hex bytes** (8 bytes primary, 8 bytes secondary).
  - Real systems may use **BCD/EBCDIC**; we’ll mention this caveat in the narration.
- Example **MTI**: `0200` (financial request).  
- Example **DEs included**: **2** (PAN, LLVAR), **4** (amount, fixed 12), **7** (transmission date & time, MMDDhhmmss).  
- We **set bit 1** to illustrate the **secondary bitmap presence**.

---

## Canonical example payload (for the visuals)

> This is **for display only**; no parsing code here—just the bytes you will **draw** and **highlight**.

### Human-readable segmentation

- **MTI** (ASCII): `0200`
- **Primary bitmap** (hex, 8 bytes): `D2 00 00 00 00 00 00 00`  
  - Bits set (1-based): **1**, **2**, **4**, **7**
- **Secondary bitmap** (hex, 8 bytes): `00 00 00 00 00 00 00 00` (present because bit 1 = 1)
- **DE 2** (PAN, **LLVAR**): length `16` + `4539681234567890`  
  - ASCII bytes: `31 36` + `34 35 33 39 36 38 31 32 33 34 35 36 37 38 39 30`
- **DE 4** (Amount, **fixed 12**): `000000001000` (for example **$10.00** in minor units)  
  - ASCII bytes: `30 30 30 30 30 30 30 30 31 30 30 30`
- **DE 7** (Transmission date & time, **fixed 10**): `1013123039` (MMDDhhmmss)  
  - ASCII bytes: `31 30 31 33 31 32 33 30 33 39`

### Entire message (no network length prefix)

- **Total length:** 60 bytes  
- **Hex (continuous):**  
  `30 32 30 30 D2 00 00 00 00 00 00 00 00 00 00 00 00 00 31 36 34 35 33 39 36 38 31 32 33 34 35 36 37 38 39 30 30 30 30 30 30 30 30 31 30 30 30 31 30 31 33 31 32 33 30 33 39`

### Length prefix for sockets (added later in the animation)

- **Binary 2-byte big-endian length header** (example): `00 3C` (60 bytes)
- Transmission frame (for the final scene):  
  `00 3C | 30 32 30 30 | D2 00 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00 | 31 36 ... 33 39`

---

## Script & storyboard (scene by scene)

### 0) Cold open (2–3 s)
- **Visual:** Title card slides in: “**ISO 8583 in 10 Minutes**”. Subline: “Messages behind card payments.”
- **VO:** “ISO 8583 is an old, battle-tested standard that still powers card payments today. In a few minutes, let’s read one message together.”

---

### 1) What is ISO 8583? (10–15 s)
- **Visual:** Standard name appears; quick timeline marker “1987 → today”.
- **On-screen text:** “**Goal:** Understand the message format.”
- **On-screen text:** “ISO 8583 defines how payment systems talk—authorization, financial transactions, reversals, network management—using a compact message layout.”

---

### 2) Meet the message (15–20 s)
- **Visual:** A horizontal “packet strip” fades in, left-to-right blocks labeled:
  - `MTI` | `Primary Bitmap` | `Secondary Bitmap` | `DE 2` | `DE 4` | `DE 7`
- The **hex/ASCII bytes** for each segment appear beneath each block (see example above).
- Do not overlap the block text with the message
- Mainain the message aligned and with the same font 
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
- **DE 2 (LLVAR) animation:**
  - Brace around `31 36` with label “**length = 16**”.
  - Then highlight `4539681234567890` as the **value**.
  - Caption: “**DE 2 — PAN (LLVAR)**”.
- **DE 4 (fixed 12) animation:**
  - Brace the whole `000000001000` with label “**12 digits**”.
  - Caption: “**DE 4 — Amount (N 12)**”.
- **VO:** “Variable-length fields prefix their length—LLVAR uses two digits, LLLVAR uses three. Fixed fields always consume a known size.”

---

### 7) Another fixed example (10–12 s)
- **Visual:** Highlight **DE 7**: `1013123039` with annotation “**MMDDhhmmss**”.
- **Caption:** “**DE 7 — Transmission date & time (N 10)**”.
- **VO:** “DE 7 is a timestamp—month, day, hour, minute, second—useful for clocks and reconciliation.”

---

### 8) Data types cheat-sheet (10–15 s)
- **Visual:** Compact grid of tags with micro-examples:
  - **N** (numeric), **AN** (alphanumeric), **ANS** (printable), **B** (binary), **Z** (track data), **LLVAR/LLLVAR** (variable).
- **VO:** “You’ll meet numeric, alphanumeric, printable, and binary fields. Track data and variable-length types are common in POS flows.”

---

### 9) On the wire — length prefix & sockets (20–30 s)
- **Visual:** The original message collapses into a compact block. A **purple** 2-byte header appears to its **left**: `00 3C`.  
  - Label: “**2-byte big-endian length (60)**”.
- Cut to a **network line**: POS/Client → **Socket** → Host.  
- The frame `00 3C | …message…` travels across.
- **VO:** “Over TCP sockets, messages are framed with a length header—here, `00 3C` for 60 bytes. Some stacks add ISO headers or use 4 bytes, but the idea is the same: frame, send, parse.”

---

### 10) Recap & pointers (10–15 s)
- **Visual:** Quick checklist ticks:
  - MTI classifies the message
  - Bitmap lists present fields
  - Fixed vs variable elements
  - Length prefix for transport
- **VO:** “Now you can read an ISO 8583 at a glance. MTI tells you the intent; bitmaps tell you which fields are here; and a tiny length header keeps it moving across the wire.”

---

## Optional appendices (use if time permits or as post-roll cards)

- **Common DEs to recognize quickly:**  
  `3` Processing Code, `7` Transmission Date/Time, `11` STAN, `12/13` Local Time/Date, `37` RRN, `39` Response Code, `41/42` Terminal/Merchant IDs.
- **MTI quick table:**  
  `0100/0110` Auth, `0200/0210` Financial, `0400/0410` Reversal, `0800/0810` Network.
- **Encoding caveat:** Real deployments may use **BCD/EBCDIC**, **packed** numeric fields, and **ISO headers** (e.g., TPDU), which change the exact bytes—not the **concepts**.

---

## On-screen text (exact strings to display)

Use these as labels/captions in the shots:

- “ISO 8583 — Still powering card payments”
- “Goal: Understand the message format”
- “MTI = 0200 (Financial Request)”
- “Primary Bitmap (8 bytes)”
- “Bit 1 = Secondary bitmap present”
- “DE 2 present” / “DE 4 present” / “DE 7 present”
- “Secondary Bitmap (fields 65–128)”
- “DE 2 — PAN (LLVAR): length + value”
- “DE 4 — Amount (N 12)”
- “DE 7 — Transmission date & time (N 10)”
- “Variable length: LLVAR/LLLVAR”
- “On the wire: 2-byte length prefix”
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

## Animation notes & suggestions (no code)

- Use **focus rectangles** and **braces** to tie labels to byte runs.
- When revealing the **first bitmap byte** (`D2`), morph it into **binary** (`11010010`) and **pulse** the bits that are `1`.  
  Simultaneously **blink** the corresponding DE blocks (2, 4, 7) and the **secondary bitmap** block for bit 1.
- For **LLVAR**, animate the **length** “lifting” out of the field, then the **value** slides in behind it.
- Keep **camera moves** slow; rely on **color** and **isolation** to direct attention.
- When showing the **length prefix**, briefly show the **decimal** `(60)` next to `00 3C`.

---

## Narration (one-take draft)

> “ISO 8583 is an old, battle-tested standard still powering card payments. In this short video we’ll read one message together. An ISO 8583 message starts with an MTI—the Message Type Identifier—followed by one or two bitmaps that tell us which data elements are present, and then the data elements themselves.  
>  
> This MTI is ‘0200’, a financial request. Pair it with ‘0210’ for the response. You’ll also see ‘0100/0110’ for authorization, and ‘0800/0810’ for network management.  
>  
> The bitmap is a map of presence bits. In the first byte, 11010010 means bit 1 is set—so a secondary bitmap follows—and bits 2, 4, and 7 are set, which means include DE 2, DE 4, and DE 7.  
>  
> Data elements can be fixed or variable length. DE 2, the primary account number, is LLVAR: two digits of length, then the value. DE 4, the amount, is fixed to 12 numeric characters. DE 7, transmission date and time, is a fixed 10-digit timestamp.  
>  
> Over the network, messages are framed with a small length header—here, two bytes, big-endian. Our 60-byte message is prefixed with 00 3C, sent over a TCP socket, and parsed on the other side.  
>  
> That’s the core of ISO 8583: MTI to classify, bitmaps to declare, fields to carry the data, and a tiny prefix to keep it moving across the wire.”

---

## Credits & caveats card (end slate)

- “Encodings simplified for clarity (ASCII digits, hex bitmaps). Real systems often use **BCD**, **EBCDIC**, **ISO headers**, and dialect-specific field sets.”
- “MTI/data elements may vary by network and spec version.”

---

## (Optional) What to parameterize later (if you decide to auto-generate variants)

- **MTI pairs** to cycle through (0100/0110, 0200/0210, 0400/0410, 0800/0810).
- **Bitmaps** to toggle different DEs.
- **DE examples** (11 STAN, 37 RRN, 39 Response Code) for response messages.
- **Length framing** style (2 bytes vs 4 bytes; big- vs little-endian; TPDU/ISO header presence).

---

### Ready-to-draw byte cheat sheet (copy into your artwork)

- **MTI**: `30 32 30 30` (ASCII “0200”)  
- **Primary bitmap**: `D2 00 00 00 00 00 00 00`  
- **Secondary bitmap**: `00 00 00 00 00 00 00 00`  
- **DE 2 (LLVAR)**: `31 36 34 35 33 39 36 38 31 32 33 34 35 36 37 38 39 30`  
- **DE 4 (N12)**: `30 30 30 30 30 30 30 30 31 30 30 30`  
- **DE 7 (N10)**: `31 30 31 33 31 32 33 30 33 39`  
- **2-byte length (network)**: `00 3C` (prepend for the socket scene)
