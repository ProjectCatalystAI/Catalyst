// Catalyst — flow data. Plausible fictional catalogues so the product feels real.
window.FLOW_DATA = {
  pm: "M. Okoye",
  org: "Concord · Catalogue, US",
  catalogues: [
    {
      id: "c-italo-vol-2",
      name: "Italo Heritage, Vol. II",
      meta: { tracks: 142, years: "1968 — 1989", region: "IT", last: "2026-04-22" },
      summary: "A second tranche of acquired Italian pop and cantautore titles — heavy on spring and summer single material from RCA Italiana and Numero Uno. Strong sync history in EU fashion and Italian-language film.",
      selected: true,
      narrowing: {
        applied: ["pre-1985", "Italian-language", "tempo 88-128"],
        kept: 84,
        of: 142
      }
    },
    {
      id: "c-rae",
      name: "Rae Kellman · Master Recordings",
      meta: { tracks: 38, years: "1996 — 2011", region: "US", last: "2026-05-04" },
      summary: "Singer-songwriter masters bought from the artist's estate in 2024. Adult-contemporary editorial fit; modest but consistent passive streaming on three album cuts."
    },
    {
      id: "c-southern-soul",
      name: "Southern Soul Independents (Mosley)",
      meta: { tracks: 311, years: "1962 — 1979", region: "US-South", last: "2026-03-11" },
      summary: "Catalogue acquired from Mosley Records administration. Deep, under-monetised vault — 80% of titles have not been activated since acquisition."
    },
    {
      id: "c-pines",
      name: "Pines County Trio · Complete Works",
      meta: { tracks: 67, years: "1976 — 1988", region: "US", last: "2026-05-09" },
      summary: "Country-rock complete recordings including unreleased Asheville sessions. One title currently trending on TikTok via an unsanctioned cover."
    },
    {
      id: "c-junie",
      name: "Junie Adair · Atlantic Years",
      meta: { tracks: 54, years: "1989 — 1998", region: "US", last: "2026-02-28" },
      summary: "Atlantic-era recordings under recent licensing review. Strongest sync candidates concentrated on the second and fourth albums."
    }
  ],

  // Seasonal moment results
  seasonal: {
    catalogue: "Italo Heritage, Vol. II",
    moment: "Spring · Northern Hemisphere",
    daysUntil: 18,
    flaggedCount: 9,
    totalCount: 84,
    tracks: [
      { id: 1, lit: true,  rank: 1, title: "Maledetta Primavera", artist: "Loretta Marini", year: 1981, isrc: "ITRC8100412", reason: "Spring begins in 18 days. Track is the most-streamed Italian spring-themed catalogue title with seasonal activation patterns recorded in three of the last four years (Mar 12 — Apr 28). 2025 lift was +41% over baseline; current pre-window movement is already +6%." },
      { id: 2, lit: true,  rank: 2, title: "Aprile, una mattina",  artist: "Gianni Solare", year: 1974 },
      { id: 3, lit: true,  rank: 3, title: "Tornano i mandorli",   artist: "Loretta Marini", year: 1978 },
      { id: 4, lit: true,  rank: 4, title: "Maggio bianco",        artist: "I Quattro Venti", year: 1969 },
      { id: 5, lit: true,  rank: 5, title: "Il primo sole",        artist: "Carla Vento",    year: 1983 },
      { id: 6, lit: true,  rank: 6, title: "La domenica di Pasqua", artist: "Gianni Solare", year: 1971 },
      { id: 7, lit: true,  rank: 7, title: "Primavera in città",   artist: "Tomaso Briganti", year: 1976 },
      { id: 8, lit: true,  rank: 8, title: "Caldo aprile",         artist: "I Quattro Venti", year: 1972 },
      { id: 9, lit: true,  rank: 9, title: "Il fiore di mio padre", artist: "Loretta Marini", year: 1986 },
      { id: 10, lit: false, title: "Notte d'agosto",               artist: "Tomaso Briganti", year: 1979 },
      { id: 11, lit: false, title: "L'autunno è arrivato",         artist: "Carla Vento",    year: 1984 },
      { id: 12, lit: false, title: "Inverno a Trieste",            artist: "Gianni Solare",  year: 1968 },
      { id: 13, lit: false, title: "Domenica sera",                artist: "Loretta Marini", year: 1973 },
      { id: 14, lit: false, title: "Vento del nord",               artist: "I Quattro Venti", year: 1970 },
      { id: 15, lit: false, title: "Dicembre, mai più",            artist: "Tomaso Briganti", year: 1988 },
      { id: 16, lit: false, title: "Foglie di settembre",          artist: "Carla Vento",    year: 1981 },
      { id: 17, lit: false, title: "Il porto chiuso",              artist: "Gianni Solare",  year: 1975 }
    ]
  },

  // Social trend results
  social: {
    catalogue: "Italo Heritage, Vol. II",
    artists: [
      { id: "marini",   name: "Loretta Marini",     lit: true,  tracks: 22, lifeyears: "1962 — 1994", flagged: 4 },
      { id: "solare",   name: "Gianni Solare",      lit: true,  tracks: 18, lifeyears: "1965 — 2001", flagged: 2 },
      { id: "vento",    name: "Carla Vento",        lit: true,  tracks: 14, lifeyears: "1971 — 1990", flagged: 1 },
      { id: "quattro",  name: "I Quattro Venti",    lit: false, tracks: 11, lifeyears: "1968 — 1981", flagged: 0 },
      { id: "briganti", name: "Tomaso Briganti",    lit: true,  tracks: 9,  lifeyears: "1969 — 1995", flagged: 2 },
      { id: "armano",   name: "Renzo Armano",       lit: false, tracks: 6,  lifeyears: "1970 — 1983", flagged: 0 },
      { id: "ricci",    name: "Sergio Ricci & Lina", lit: false, tracks: 4, lifeyears: "1973 — 1979", flagged: 0 }
    ],
    // Selected artist for the artist view
    selectedArtist: {
      id: "marini",
      name: "Loretta Marini",
      meta: "Italian · 1962 — 1994 · 22 selected tracks · 4 flagged",
      overall: "Marini's catalogue is in an active rediscovery cycle on TikTok and Reels, led by a 22-year-old cover community in Lombardy. Reuse of original masters (not cover audio) is accelerating week-over-week; YouTube long-form is flat. Concentrate activation on the four flagged Spring titles within the next 21 days.",
      ig: {
        followers: "—", note: "no managed profile",
        summary: "Audio reuse on Reels grew 38% week-over-week. The cover-community handle @leila.s is driving 72% of audio mentions; reuse correlates strongest with original-master streams (r 0.81).",
        tags: ["audio reuse", "cover community", "lombardy"]
      },
      tt: {
        followers: "—", note: "no managed profile",
        summary: "TikTok creator count using Marini's catalogue audio reached 1.8k this week, up from 412 four weeks ago. The trending sound is a 9-second hook from 'Maledetta Primavera' aligned with a spring routine.",
        tags: ["sound · 9s", "spring routine", "ages 18-24"]
      },
      yt: {
        followers: "412k", note: "official artist channel",
        summary: "Long-form views flat at 1.2M / 28d. YouTube Shorts seeded from the IG / TikTok activity are converting to channel watch time at 0.6× the platform average — modest.",
        tags: ["shorts seeding", "flat long-form"]
      },
      tracks: [
        { id: 1, title: "Maledetta Primavera", year: 1981, lit: true, selected: true },
        { id: 9, title: "Il fiore di mio padre", year: 1986, lit: true },
        { id: 3, title: "Tornano i mandorli", year: 1978, lit: true },
        { id: 13, title: "Domenica sera", year: 1973, lit: false },
        { id: 22, title: "Notte di luna piena", year: 1969, lit: false },
        { id: 18, title: "Lettera da Trento", year: 1989, lit: false }
      ]
    },
    // Selected track view (drills into Maledetta Primavera)
    selectedTrack: {
      id: 1,
      title: "Maledetta Primavera",
      artist: "Loretta Marini",
      year: 1981,
      isrc: "ITRC8100412",
      overall: "Original-master reuse is the dominant signal. Cover audio still leads volume, but the conversion from cover-impression to original-master stream sits at 6.2× the platform baseline — the highest in this catalogue this quarter. Track is the seasonal anchor across all three platforms.",
      ig: {
        videos: [
          { handle: "@leila.s",          desc: "acoustic cover, garden",       views: "1.4M", corr: 0.81 },
          { handle: "@sundownsessions",  desc: "audio reuse · piano",          views: "612k", corr: 0.68 },
          { handle: "@nona.in.fiore",    desc: "spring routine, grandmother",  views: "488k", corr: 0.62 },
          { handle: "@trento_mornings",  desc: "city walk · original audio",   views: "311k", corr: 0.59 },
          { handle: "@cleo.cantante",    desc: "duet stitch · daughter",       views: "224k", corr: 0.55 }
        ]
      },
      tt: {
        videos: [
          { handle: "@leila.s",        desc: "cover, 9-second hook",            views: "3.1M", corr: 0.83 },
          { handle: "@valle.lombarda", desc: "spring run routine, original",    views: "1.2M", corr: 0.71 },
          { handle: "@chiave_di_sol",  desc: "duet, voice-only",                views: "844k", corr: 0.66 },
          { handle: "@nico.fava",      desc: "drive POV, original",             views: "601k", corr: 0.61 },
          { handle: "@magnoliepark",   desc: "blossom timelapse, original",     views: "418k", corr: 0.58 }
        ]
      },
      yt: {
        videos: [
          { handle: "Pines & Hollow",      desc: "song walk-through, 4K",         views: "84k", corr: 0.54 },
          { handle: "Italo Originale",     desc: "audio remaster upload, 1981",   views: "62k", corr: 0.48 },
          { handle: "Vinyl Hour · IT",     desc: "side B listen-through",         views: "39k", corr: 0.41 },
          { handle: "Marini Estate",      desc: "official master · audio only",   views: "28k", corr: 0.38 },
          { handle: "Domenica Live",       desc: "vintage TV performance, 1981",  views: "21k", corr: 0.34 }
        ]
      },
      shorts: {
        videos: [
          { handle: "@leila.s",       desc: "60s vertical cover",            views: "412k", corr: 0.79 },
          { handle: "Italo Originale",desc: "audio short with lyric card",   views: "188k", corr: 0.62 },
          { handle: "@trento_mornings", desc: "spring city short",            views: "144k", corr: 0.57 },
          { handle: "Marini Estate", desc: "official short · cover art",     views: "92k",  corr: 0.49 },
          { handle: "@nona.in.fiore",desc: "garden short, original",         views: "61k",  corr: 0.43 }
        ]
      }
    }
  }
};
