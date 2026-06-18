#!/usr/bin/env python3
"""
compress.py - Shrink the support-assistant-prototype.html for constrained widget rendering.
Replaces repeated SVG blobs with short placeholder spans, then appends a JS block
that swaps them back after page load.
"""

INPUT  = '/sessions/sleepy-focused-babbage/mnt/outputs/support-assistant-prototype.html'
OUTPUT = '/sessions/sleepy-focused-babbage/mnt/outputs/widget_compact.html'

# ── The four SVG strings to replace ──────────────────────────────────────────

LOGO = (
    '<svg class="sign-ico" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    '<path d="M12 0C5.38963 0 0 5.38964 0 12C0 18.6104 5.38963 24 12 24C18.6103 24 24 18.6104 24 12C24 5.3666 18.6103 0 12 0Z" fill="#0E5BF3"/>'
    '<path d="M13.405 5.13608L6.77165 13.6581C6.74861 13.7042 6.72559 13.7272 6.72559 13.7733V14.7407C6.72559 14.8558 6.81771 14.948 6.93288 14.948H12.8753C12.9904 14.948 13.0826 15.0401 13.0826 15.1553V18.6102C13.0826 18.7253 13.1747 18.8175 13.2899 18.8175H14.5567C14.6718 18.8175 14.764 18.7253 14.764 18.6102V5.25124C14.764 5.13608 14.6718 5.04395 14.5567 5.04395H13.5893C13.5202 5.06698 13.4511 5.09001 13.405 5.13608ZM8.98278 13.1054L12.7141 8.33761C12.8292 8.17638 13.0826 8.26851 13.0826 8.45277V13.2205C13.0826 13.3357 12.9904 13.4278 12.8753 13.4278H9.14401C8.95975 13.4509 8.86761 13.2436 8.98278 13.1054Z" fill="white"/>'
    '</svg>'
)

LOGO_INVIS = (
    '<svg class="sign-ico" style="opacity:0" width="24" height="24" viewBox="0 0 24 24"></svg>'
)

HDR_DOTS = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="rgba(0,0,0,0.54)">'
    '<path d="M6 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm12 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-6 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>'
    '</svg>'
)

HDR_CHEV = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="rgba(0,0,0,0.54)">'
    '<path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/>'
    '</svg>'
)

# ── Placeholder spans ─────────────────────────────────────────────────────────

PH_LOGO       = '<span class="ico-logo"></span>'
PH_LOGO_INVIS = '<span class="ico-logo-invis"></span>'
PH_DOTS       = '<span class="ico-dots"></span>'
PH_CHEV       = '<span class="ico-chev"></span>'

# ── JS restore block (injected before </body>) ────────────────────────────────

JS_BLOCK = """<script>
(function(){
  var svgs={
    'ico-logo': '<svg class="sign-ico" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 0C5.38963 0 0 5.38964 0 12C0 18.6104 5.38963 24 12 24C18.6103 24 24 18.6104 24 12C24 5.3666 18.6103 0 12 0Z" fill="#0E5BF3"/><path d="M13.405 5.13608L6.77165 13.6581C6.74861 13.7042 6.72559 13.7272 6.72559 13.7733V14.7407C6.72559 14.8558 6.81771 14.948 6.93288 14.948H12.8753C12.9904 14.948 13.0826 15.0401 13.0826 15.1553V18.6102C13.0826 18.7253 13.1747 18.8175 13.2899 18.8175H14.5567C14.6718 18.8175 14.764 18.7253 14.764 18.6102V5.25124C14.764 5.13608 14.6718 5.04395 14.5567 5.04395H13.5893C13.5202 5.06698 13.4511 5.09001 13.405 5.13608ZM8.98278 13.1054L12.7141 8.33761C12.8292 8.17638 13.0826 8.26851 13.0826 8.45277V13.2205C13.0826 13.3357 12.9904 13.4278 12.8753 13.4278H9.14401C8.95975 13.4509 8.86761 13.2436 8.98278 13.1054Z" fill="white"/></svg>',
    'ico-logo-invis': '<svg class="sign-ico" style="opacity:0" width="24" height="24" viewBox="0 0 24 24"></svg>',
    'ico-dots': '<svg width="20" height="20" viewBox="0 0 24 24" fill="rgba(0,0,0,0.54)"><path d="M6 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm12 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-6 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>',
    'ico-chev': '<svg width="20" height="20" viewBox="0 0 24 24" fill="rgba(0,0,0,0.54)"><path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg>'
  };
  Object.keys(svgs).forEach(function(cls){
    var spans=document.querySelectorAll('span.'+cls);
    var tmp=document.createElement('div');
    tmp.innerHTML=svgs[cls];
    var tpl=tmp.firstChild;
    spans.forEach(function(s){s.parentNode.replaceChild(tpl.cloneNode(true),s);});
  });
})();
</script>"""

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        html = f.read()

    original_size = len(html.encode('utf-8'))

    # Count before replacing (for reporting)
    counts = {
        'logo':       html.count(LOGO),
        'logo_invis': html.count(LOGO_INVIS),
        'dots':       html.count(HDR_DOTS),
        'chev':       html.count(HDR_CHEV),
    }

    # Replace LOGO_INVIS before LOGO — both share the '<svg class="sign-ico"' prefix;
    # doing invis first avoids any partial-match concern.
    html = html.replace(LOGO_INVIS, PH_LOGO_INVIS)
    html = html.replace(LOGO,       PH_LOGO)
    html = html.replace(HDR_DOTS,   PH_DOTS)
    html = html.replace(HDR_CHEV,   PH_CHEV)

    # Inject JS restore block just before </body>
    if '</body>' in html:
        html = html.replace('</body>', JS_BLOCK + '\n</body>', 1)
    else:
        html += JS_BLOCK

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)

    final_size = len(html.encode('utf-8'))

    print(f"Input file : {INPUT}")
    print(f"Output file: {OUTPUT}")
    print()
    print(f"SVG occurrences replaced:")
    for k, v in counts.items():
        print(f"  {k:12s}: {v}")
    print()
    print(f"Original size : {original_size:,} bytes")
    print(f"Final size    : {final_size:,} bytes")
    print(f"Reduction     : {original_size - final_size:,} bytes  ({100*(original_size-final_size)/original_size:.1f}%)")

if __name__ == '__main__':
    main()
