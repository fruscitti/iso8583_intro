# ISO 8583 with jPOS — Manim Animation Script (Part 2: jPOS Deep‑Dive, *no code to run*)

> This add‑on extends the previous ISO 8583 animation with **jPOS** concepts: `ISOMsg`, Packagers, composite subfields, Channels, and `QMUX`. All examples are storyboarded for on‑screen visuals/VO, not executable code.

---

## Learning goals (this part)

1) Know what **jPOS** is and why it’s widely used in ISO 8583 stacks.  
2) Read and **compose messages with `ISOMsg`** and understand its **Composite** design.  
3) Understand **Packagers** (how they map fields → bytes) including simple, LLVAR, and **composite** subfields.  
4) See what **Channels** are for, with examples (ASCIIChannel, SSL, Loopback).  
5) Grasp how **`QMUX`** correlates requests and responses on one socket.

---

## Scene J0 — Intro to jPOS (8–12 s)

**Visuals**  
- Logo/title card: “**jPOS** — ISO 8583 toolkit for Java”.  
- Small highlights fly in: “ISOMsg”, “Packagers”, “Channels”, “MUX/QMUX”.  
- Ribbon note: “Available on Maven Central” (brief).

**On‑screen bullets (short):**  
- “**Mature & modular** ISO 8583 toolkit”  
- “Pluggable **packagers** & **channels**”  
- “**Multiplexing (QMUX)** for request/response over one socket”  
- “Published to **Maven Central**”

**VO**  
“jPOS is a mature, modular toolkit for ISO 8583. It gives you `ISOMsg` for structure, packagers to pack/unpack bytes, channels to move messages on the wire, and a multiplexer (`QMUX`) to correlate responses—available as a dependency from Maven Central.”

> Source cues: Maven Central usage and Gradle/Maven snippets; jPOS components overview. fileciteturn2file4L42-L61

---

## Scene J1 — `ISOMsg` uses the **Composite pattern** (20–25 s)

**Visuals**  
- Bring in a **diagram** inspired by the guide’s *“ISOMsg & Co.”* page: a tree where **ISOMsg** and **ISOField/ISOBitMapField/ISOBinaryField** are all **`ISOComponent`** nodes. Animate leaves vs. composites.  
- Focus box on `ISOComponent` essential methods (pack/unpack, getChildren, etc.).

**VO**  
“In jPOS, an ISO 8583 message is an `ISOMsg`. It uses the **Composite pattern**—the same abstraction backs the message and each field. This lets you nest messages and treat fields uniformly.”

**On‑screen labels**  
- “`ISOComponent` → common API”  
- “`ISOMsg` ← composite (has children)”  
- “`ISOField`/`ISOBitMapField`/`ISOBinaryField` ← leaves”

> Source cues: composite pattern, API methods, and the ‘ISOMsg & Co.’ diagram reference. fileciteturn1file0L56-L66 fileciteturn2file1L1-L17 fileciteturn2file1L28-L36

**Micro‑demo overlay (visual only, not runnable):**  
- Show `m.setMTI("0800")`, `m.set(3,"000000")`, `m.set(11,"000001")`, `m.set(41,"29110001")` as animated chips entering the `ISOMsg` box.  
> Source cue: helper methods (setMTI/set). fileciteturn2file1L48-L55 fileciteturn2file1L62-L69

---

## Scene J2 — What is a **Packager**? (25–30 s)

**Visuals**  
- Left: “Field spec” (e.g., Field 4 = N12, Field 2 = LLVAR N up to 19, Field 3 = N6).  
- Right: “Bytes out” as a hex strip.  
- Animate the **peer** relationship: `ISOMsg.pack()` → **delegates** to `ISOPackager` → to `ISOFieldPackager` per field type.

**VO**  
“A **Packager** knows how to turn an `ISOMsg` into bytes and back. `ISOMsg.pack()` delegates to its `ISOPackager`, which uses a specific `ISOFieldPackager` for each field.”

> Source cues: delegation from ISOMsg to packager and field packagers. fileciteturn2file3L1-L10

**On‑screen flashcard:**  
- Field packager families: `IFA_NUMERIC` (fixed ASCII), `IFB_NUMERIC` (fixed BCD), `IFB_LLNUM` (LLVAR BCD), etc.  
> Source cue: table of ISOFieldPackagers. fileciteturn2file2L14-L32

---

## Scene J3 — Defining a Packager (15–20 s)

**Visuals**  
- Slide in an **XML** packager (no full code): IDs 0..6 with classes like `IFA_NUMERIC`, `IFA_BITMAP`, `IFA_LLNUM`. Key lines highlight.  
- Caption: “`GenericPackager` can be configured with XML”.

**VO**  
“You can extend `ISOBasePackager` in Java, or use `GenericPackager` with a concise **XML** spec that maps each DE to a field type and length.”

> Source cues: custom packagers, `ISOBasePackager` snippet, and `GenericPackager` XML example. fileciteturn2file2L53-L71 fileciteturn1file4L36-L45 fileciteturn1file4L47-L56

---

## Scene J4 — **Composite subfields** (DE 3 as 3×2‑digit parts) (25–35 s)

**Visuals**  
- Bring field **3 Processing Code** forward. It **explodes** into **three sub‑fields**:  
  1) “Transaction Code” (2)  
  2) “Account‑From” (2)  
  3) “Account‑To” (2)  
- Show an XML **sub‑packager** badge: `packager="org.jpos.iso.packager.GenericSubFieldPackager"` (the exact lines appear as an overlay).  
- Animate user setting subfield values individually; the packager **recombines** them into DE 3 (N6).

**VO**  
“Because `ISOMsg` is composite, a field can itself hold sub‑fields. With `GenericPackager`, you define field 3 as a **container** with a **sub‑packager**; at pack time, the sub‑components render into the parent field’s bytes.”

> Source cues: Composite design, custom packager definitions, GenericPackager XML. fileciteturn1file0L60-L66 fileciteturn2file2L53-L71 fileciteturn1file4L69-L77

**Note for the artist**  
- Reuse the user’s XML structure for the on‑screen snippet (field 3 has an `isofieldpackager` with 3 inner `isofield`s).  
- When values are entered (e.g., “00|00|00”), show the packed N6 as **3 BCD bytes** if the chosen `IFB_NUMERIC` is used.

---

## Scene J5 — Byte‑by‑byte packing vignette (30–40 s)

**Goal**: **Make the encoding visible.** Show three quick cuts:
1) **Simple fixed field:** MTI. On‑screen toggle: “`IFA_NUMERIC` 4 digits (ASCII) → `30 31 30 30` for ‘0100’” vs “`IFB_NUMERIC` 4 digits (BCD) → `01 00`”.  
2) **Composite field:** DE 3 from Scene J4: 6 digits “`00 00 00`” → show **3 packed bytes**.  
3) **LLVAR numeric:** DE 2 PAN (e.g., 16 digits). Show **1‑byte BCD length** (`0x16`) + **packed digits** (2 per byte).

**VO**  
“The packager type determines the on‑wire bytes. ASCII families write digits as characters; BCD families pack **two digits per byte**. LLVAR prefixes the digit count, often in BCD.”

> Source cues: field packager families and pack/unpack responsibilities. fileciteturn2file3L8-L13 fileciteturn2file2L26-L32

---

## Scene J6 — **Channels** (purpose + examples) (20–25 s)

**Visuals**  
- A socket icon between **Client** and **Host**.  
- Left overlay: “ASCIIChannel: **4‑byte length** + message”.  
- Other badges popping: “SSL Channel”, “LoopbackChannel (testing)”.  
- Quick tip bubble on **PADChannel** and message boundaries.

**VO**  
“A **Channel** encapsulates the wire protocol. jPOS ships many: e.g., **ASCIIChannel** frames with a 4‑byte length, **SSL** channels add TLS, and **LoopbackChannel** is great for tests. Some stacks use older, packet‑assumed flows—`PADChannel` explains MTU and boundary issues.”

> Source cues: ISOChannel interface purpose and sample implementations list. fileciteturn1file3L14-L22 fileciteturn1file3L24-L36 fileciteturn1file3L44-L59

---

## Scene J7 — **QMUX**: correlate responses on one socket (35–45 s)

**Visuals**  
- Show a single channel pipe. Multiple requests (`R1`, `R2`, `R3`) enter a **Queue**.  
- Each gets tagged with a **Key** (e.g., fields **41+11**).  
- Responses return out of order; the **Key** matches them to the **waiting thread**; unmatched traffic drops to an **ISORequestListener** or **Space** queue.

**VO**  
“`MUX` multiplexes a single channel. `QMUX` lets you `request(m, timeout)` and waits for the match. It uses a **key** derived from selected fields—configurable via XML—to route the response back to the caller. A common default combines **41 (Terminal ID)** + **11 (STAN)**. Asynchronous callbacks are supported too.”

**On‑screen microflow**  
- “`request(m, 30s)` → queued → channel.send”  
- “response arrives → **getKey(response)** → deliver to caller, else → listener/Space”

> Source cues: MUX interface, async request, key selection (XML `<key>…</key>`), typical fields (41+11), and unmatched handling. fileciteturn1file1L33-L41 fileciteturn1file2L12-L21 fileciteturn1file2L41-L46 fileciteturn1file2L67-L73

---

## Scene J8 — Putting it together (10–15 s)

**Visuals**  
- Stack of blocks animates into place: `ISOMsg` → Packager → **HEX bytes** → Channel → **Length prefix** (if used) → Socket.  
- Parallel path: `ISOMsg` → `QMUX` → queue → Channel → response matched by **Key**.

**VO**  
“In jPOS: you build an `ISOMsg`, the **Packager** renders bytes, a **Channel** sends them, and **`QMUX`** pairs the response. Same ideas you saw for ISO 8583—now with the toolkit that makes them production‑grade.”

---

## Appendix (for the narrator / artist)

- **ISOMsg & Composite**: emphasize nesting and uniform treatment of fields. Show the guide’s “ISOMsg & Co.” style tree on this scene.  
- **Packager families**: use consistent color coding: ASCII vs BCD vs Binary.  
- **Composite subfields**: when you animate DE 3, flash its inner IDs (“1, 2, 3”) before recombining.  
- **Channels**: put a **“4‑byte length”** label near ASCIIChannel.  
- **QMUX**: display a small `<key>41,11</key>` tag near the queue to reinforce configurability.

---

### Sources (for grounding the storyboard)

- ISOMsg Composite pattern + API & helper methods. fileciteturn1file0L56-L66 fileciteturn2file1L1-L17 fileciteturn2file1L48-L55  
- Packager delegation & families; ISOBasePackager and GenericPackager XML. fileciteturn2file3L1-L10 fileciteturn2file2L14-L32 fileciteturn2file2L53-L71 fileciteturn1file4L47-L56  
- Channels purpose & examples. fileciteturn1file3L14-L22 fileciteturn1file3L24-L36  
- QMUX correlation, async, and keys (41+11). fileciteturn1file1L33-L41 fileciteturn1file2L12-L21 fileciteturn1file2L41-L46 fileciteturn1file2L67-L73  
- Maven Central availability. fileciteturn2file4L42-L61