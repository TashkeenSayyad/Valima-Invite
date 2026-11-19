# Valima Invitation

A white-themed, single-page invitation website for the Valima reception.

- **Date:** Tuesday, 29 December 2026
- **Time:** 8:00 PM (PKT)
- **Venue:** Zam Zam Lawn, Thatta
- **Couple:** Tashkeen & Anusha

## Features

- Premium gold-foil styling with English translations under all Arabic & Sindhi text
- Desi shaadi-card styling: marigold garlands, Mughal arch, paisley (kairi) motifs, jaali pattern, Ajrak borders, Sindhi text
- "Open Invitation" card with a gold T ✦ A laurel-wreath monogram, resting on carved ivory palace doors (raised panels, jaali windows, gold studs and knocker rings, a small marigold garland). The card fades, a gold T ✦ A medallion across the seam splits in two, and the doors swing open slowly as warm light spills through and the invitation settles into view, followed by a rose, marigold & gold-flake shower
- Couple's names in Sindhi calligraphy (تاشقين ۽ انوشا)
- Textured gold-foil lettering with twinkling sparkles around the names
- Swaying golden Mughal lanterns with a warm glow
- Deep maroon countdown band with an Ajrak-inspired pattern and borders
- Monogram watermark behind the closing dua
- Bismillah, invitation text and a Nikah dua
- Live countdown to the event
- Event detail cards, Google Maps directions and embedded map
- "Add to Calendar" button (downloads an `.ics` file with a 1-day reminder)
- Personal greeting per guest via the link (`?to=Ahmed+Family`)
- Sindhi / English switch (floating button, remembered per visitor; `?lang=sd` opens in Sindhi)
- Names as the focal point, compact event-details card, arch-framed map, scalloped section edges, gentle parallax
- WhatsApp RSVP button with a pre-filled message (after setting a number)
- Background music: *Lam Yati Nazeero Kafi Nazarin* (from 1:48, just before the refrain and rhythm come in), starting when the doors open and looping softly, with a play/pause button
- Optional hosts line
- WhatsApp/social link preview image (`og-image.png`) and gold favicon
- Responsive layout for phones and desktops

## Run locally

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
```

## Publish with GitHub Pages

In the repository settings, go to **Pages**, choose **Deploy from a branch**, select the branch and `/ (root)`, and save. The site will be live at `https://<username>.github.io/Walima-Invite/`.

## Video invitation

`valima-invite.mp4` is a 17-second, 1080×1920 video of the palace doors opening and the invitation, ready for WhatsApp status or an Instagram reel, with the Sufi kalam *Lam Yati Nazeero Kafi Nazarin* as its soundtrack (timed so the rhythm comes in as the doors open).

To record it again after changes (needs Node, Playwright and ffmpeg):

```bash
node tools/record-video.js frames
```

```bash
ffmpeg -framerate 30 -i frames/f%04d.jpg -vf format=yuv420p -c:v libx264 -crf 19 -preset slow -movflags +faststart valima-invite.mp4
```

To add the song to the video (`song.mp3` = the full track):

```bash
ffmpeg -ss 105.55 -t 16.8 -i song.mp3 -af "afade=t=in:d=1.2,afade=t=out:st=14.6:d=2.2,loudnorm=I=-15" -ar 48000 music-video.wav
```

```bash
ffmpeg -framerate 30 -i frames/f%04d.jpg -i music-video.wav -vf format=yuv420p -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 160k -shortest -movflags +faststart valima-invite.mp4
```

Add a guest's name as a second argument (e.g. `"?to=Ahmed+Family"`) to record a personalised version.

## Settings

Open `script.js`; the `CONFIG` block at the top controls:

| Setting | What it does |
|---|---|
| `rsvpWhatsApp` | WhatsApp number for RSVPs, digits only in international format (e.g. `923001234567`). Empty hides the button. |
| `hosts` / `hostsSindhi` | Optional "Hosted by …" line under the names (and its Sindhi version). Empty hides it. |
| `music` | Audio file next to `index.html` (default `music.mp3`). Add the file to enable the music button; music starts when the card is opened. |

## Personal links for each guest

Add `?to=` with the guest's name to the link (use `+` for spaces):

```
https://tashkeensayyad.github.io/Walima-Invite/?to=Ahmed+Family
```

The welcome card then says "Dear Ahmed Family", and the RSVP message includes the name. Add `&lang=sd` to open the invitation in Sindhi.

## Link preview image

`og-image.png` is shown when the link is shared on WhatsApp/Facebook. Its URL in `index.html` assumes the site is published at `https://tashkeensayyad.github.io/Walima-Invite/`; update the `og:url` and `og:image` tags if it lives elsewhere. To regenerate it, open `tools/og-image.html` at 1200×630 and take a screenshot.

## Customising

Wording and colours live in `index.html` and `styles.css` (colour tokens at the top under `:root`). Sindhi versions of texts are in the `data-sd` attributes. Event times are in `script.js`.
