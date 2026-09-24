from playwright.sync_api import sync_playwright
import pathlib
p = pathlib.Path("poster.html").resolve()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    pg.goto(f"file://{p}")
    pg.wait_for_timeout(1200)
    pg.pdf(path="the_high_bank_A3.pdf", width="297mm", height="420mm",
           print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
    pg.set_viewport_size({"width":1123,"height":1587})
    pg.screenshot(path="preview.png", full_page=True)
    b.close()
print("rendered")
