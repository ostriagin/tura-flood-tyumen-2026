"""Render poster_v5.html to a one-page A3 PDF (Playwright + Chromium).

Also prints the block heights, the smallest rendered type size (the RGS
minimum is 10pt) and any images that failed to load, so the sheet can be
checked before it is submitted.
"""
from playwright.sync_api import sync_playwright
import pathlib

p = pathlib.Path("poster_v5.html").resolve()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    pg.goto(f"file://{p}"); pg.wait_for_timeout(1500)
    mm = 96 / 25.4
    tot = pg.evaluate("()=>document.querySelector('.sheet').scrollHeight") / mm
    print("CONTENT %.2f mm (sheet is 420)" % tot)
    for n, h in pg.evaluate("""()=>{const mm=96/25.4;const o=[];
        document.querySelector('.sheet').querySelectorAll(':scope > *').forEach(e=>{
          o.push([(e.className||e.tagName).toString().slice(0,20),
                  +(e.getBoundingClientRect().height/mm).toFixed(1)]);});
        return o;}"""):
        print("   %-22s%7.1f" % (n, h))
    sm = pg.evaluate("""()=>{let m=999,who='';document.querySelectorAll('*').forEach(e=>{
        if(!e.textContent.trim()||e.children.length)return;
        const f=parseFloat(getComputedStyle(e).fontSize)/(96/25.4)*2.8346;
        if(f<m){m=f;who=(e.className||e.tagName)+' :: '+e.textContent.trim().slice(0,30);}});
        return [m,who];}""")
    print("smallest text %.2f pt  <- %s" % (sm[0], sm[1]))
    print("broken images:", pg.evaluate(
        "()=>[...document.images].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src'))"))
    pg.pdf(path="out_of_downhill_A3.pdf", width="16.5354in", height="11.6929in",
           print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    pg.set_viewport_size({"width": 1587, "height": 1123})
    pg.screenshot(path="preview_v5.png", full_page=True)
    b.close()
