from playwright.sync_api import sync_playwright
import pathlib
p = pathlib.Path("poster_light.html").resolve()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    pg.goto(f"file://{p}"); pg.wait_for_timeout(1300)
    mm = 96/25.4
    parts = pg.evaluate("""()=>{const mm=96/25.4;const o=[];
      document.querySelector('.sheet').querySelectorAll(':scope > *').forEach(e=>{
        const r=e.getBoundingClientRect();
        o.push([(e.className||e.tagName).toString().slice(0,18),+(r.height/mm).toFixed(1)]);});
      return o;}""")
    tot = pg.evaluate("()=>document.querySelector('.sheet').scrollHeight")/mm
    print("TOTAL %.2f mm (target 420)"%tot)
    for n,h in parts: print(f"   {n:20s}{h:7.1f}")
    sm = pg.evaluate("""()=>{let m=999;document.querySelectorAll('*').forEach(e=>{
      if(!e.textContent.trim()||e.children.length)return;
      const f=parseFloat(getComputedStyle(e).fontSize)/(96/25.4)*2.8346;if(f<m)m=f;});return m;}""")
    print("smallest text %.2f pt"%sm)
    pg.pdf(path="the_high_bank_A3_light.pdf", width="297mm", height="420mm",
           print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
    pg.set_viewport_size({"width":1123,"height":1587})
    pg.screenshot(path="preview_light.png", full_page=True)
    b.close()
