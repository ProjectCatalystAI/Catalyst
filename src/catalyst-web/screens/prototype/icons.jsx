/* global React */

// Original monochrome platform glyphs — generic, not branded reproductions.
const PLATFORM_ICONS = {
  spotify: (s) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.6" />
      <path d="M7 10c3-1 8-1 11 1M7.5 13.5c2.5-.8 6.5-.8 9 .7M8 16.5c2-.6 5-.6 7 .5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  ),
  instagram: (s) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
      <rect x="3.5" y="3.5" width="17" height="17" rx="5" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="17" cy="7" r="1.1" fill="currentColor" />
    </svg>
  ),
  tiktok: (s) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
      <path d="M14 3v10.5a3.5 3.5 0 1 1-3.5-3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M14 3c.5 2.5 2.5 4.5 5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  ),
  youtube: (s) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
      <rect x="2.5" y="6" width="19" height="12" rx="3.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M10.5 9.5L14.5 12L10.5 14.5V9.5Z" fill="currentColor" />
    </svg>
  ),
};

function PlatformIcon({ kind, size = 14 }) {
  const renderer = PLATFORM_ICONS[kind];
  if (!renderer) return null;
  return <span className="inline-flex items-center justify-center">{renderer(size)}</span>;
}

// Indicator pill (used on row right-edge to show platform signal state)
function PlatformIndicator({ kind, on = false, pulse = false }) {
  const color = on ? (pulse ? "#00E5FF" : "#f4f4f4") : "#3a3a3a";
  const style = {
    color,
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 22,
    height: 22,
    borderRadius: 4,
  };
  if (pulse) {
    style.boxShadow = "0 0 0 1px rgba(0,229,255,0.35), 0 0 12px -2px rgba(0,229,255,0.6)";
    style.animation = "pulseDot 2.2s ease-in-out infinite";
  }
  return (
    <span style={style}>
      <PlatformIcon kind={kind} size={16} />
    </span>
  );
}

// Catalyst logo — broken C with cyan dot, matching the brand
function CatalystMark({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ marginTop: -1 }}>
      <path d="M 78 30 A 30 30 0 1 0 78 70" stroke="#f4f4f4" strokeWidth="12" strokeLinecap="round" fill="none" />
      <circle cx="78" cy="50" r="7.5" fill="#00E5FF" />
    </svg>
  );
}

// Catalyst wordmark — ported from Catalyst Cover.html.
// Open-C drawn as a stroked arc + cyan dot, followed by "atalyst"
// in Manrope ExtraBold with "at" white and "alyst" cyan.
// Measures the text bounding box once Manrope is ready, then positions
// the C so the dot reads as a counter of the letter.
function Wordmark({ height = 30 }) {
  const textRef = React.useRef(null);
  const [atalystW, setAtalystW] = React.useState(880); // estimated until measured

  React.useEffect(() => {
    let alive = true;
    const measure = () => {
      if (!alive || !textRef.current) return;
      try {
        const w = textRef.current.getBBox().width;
        if (w > 0) setAtalystW(w);
      } catch (e) {
        /* getBBox can throw if SVG not yet rendered; retry shortly */
      }
    };
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(measure);
    }
    const t1 = setTimeout(measure, 120);
    const t2 = setTimeout(measure, 600);
    return () => { alive = false; clearTimeout(t1); clearTimeout(t2); };
  }, []);

  // Construction parameters — match Cover.html exactly so the proportions
  // (stroke weight, x-height, dot diameter, kerning) are identical.
  const F = 264;                // font size in svg user units
  const xH = F * 0.530;         // Manrope ExtraBold approx x-height
  const stroke = F * 0.160;     // C stroke weight matching the type weight
  const baselineY = 600;        // arbitrary; viewBox is normalised below
  const kerning = -2;
  const cWidth = xH;            // visual width of the C = its diameter
  const cOuterR = xH / 2;
  const cCenterR = cOuterR - stroke / 2;
  const cCy = baselineY - xH / 2;

  const totalW = cWidth + kerning + atalystW;
  const cCx = cOuterR;
  const a = Math.PI / 4;        // 45° opening on the right
  const x1 = cCx + cCenterR * Math.cos(-a);
  const y1 = cCy + cCenterR * Math.sin(-a);
  const x2 = cCx + cCenterR * Math.cos(a);
  const y2 = cCy + cCenterR * Math.sin(a);
  const cPath = `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${cCenterR.toFixed(2)} ${cCenterR.toFixed(2)} 0 1 0 ${x2.toFixed(2)} ${y2.toFixed(2)}`;

  const dotR = stroke / 2;
  const dotCx = cCx + cCenterR;
  const dotCy = cCy;

  // Tight viewBox around glyphs — leave room for the dot halo on the right.
  const vbTop = baselineY - F * 0.78;
  const vbHeight = F * 0.92;
  const haloR = dotR * 2.6;
  const vbWidth = totalW + haloR;

  return (
    <svg
      height={height}
      viewBox={`${-haloR * 0.2} ${vbTop} ${vbWidth + haloR * 0.4} ${vbHeight}`}
      style={{ display: "block", overflow: "visible" }}
      aria-label="Catalyst"
    >
      <text
        ref={textRef}
        x={cWidth + kerning}
        y={baselineY}
        fontFamily="Manrope, system-ui, sans-serif"
        fontWeight="800"
        fontSize={F}
        letterSpacing={-2}
        style={{ dominantBaseline: "alphabetic" }}
      >
        <tspan fill="#ffffff">at</tspan>
        <tspan fill="#00E5FF">alyst</tspan>
      </text>
      <path d={cPath} stroke="#ffffff" strokeWidth={stroke} strokeLinecap="round" fill="none" />
      <circle cx={dotCx} cy={dotCy} r={haloR} fill="#00E5FF" opacity="0.4" style={{ filter: "blur(10px)" }} />
      <circle cx={dotCx} cy={dotCy} r={dotR} fill="#00E5FF" />
    </svg>
  );
}

window.PlatformIcon = PlatformIcon;
window.PlatformIndicator = PlatformIndicator;
window.CatalystMark = CatalystMark;
window.Wordmark = Wordmark;
