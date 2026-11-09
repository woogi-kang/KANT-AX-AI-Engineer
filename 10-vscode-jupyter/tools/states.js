// Moves things on a slide from one step to the next (10): a selection bar slides down, [ ] becomes [1].
// Runs inside the slide player as function(sec, api). gen.py inlines this file into slides that use data-st.
// The HTML is drawn in its last state, so the PDF shows the finished picture. data-st holds the earlier states:
// data-st='{"1": {"css": "top:400px", "html": "[ ]"}, "2": {...}}' means "before step 1 use this, before step 2 that".
const items = [...sec.querySelectorAll('[data-st]')].map(el => ({
  el, st: JSON.parse(el.getAttribute('data-st')), css: el.style.cssText, html: el.innerHTML,
}));
function at(n, animate) {
  for (const o of items) {
    const k = Object.keys(o.st).map(Number).filter(k => k > n).sort((a, b) => a - b)[0];
    const s = k === undefined ? null : o.st[k];
    const css = o.css + (s && s.css ? ';' + s.css : '');
    const html = s && s.html !== undefined ? s.html : o.html;
    const changed = html !== o.el.innerHTML;
    if (animate) o.el.style.cssText = css;
    else { o.el.style.cssText = css + ';transition:none'; void o.el.offsetWidth; o.el.style.cssText = css; }
    if (changed) {
      o.el.innerHTML = html;
      if (animate) o.el.animate([{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'none' }], { duration: 380, easing: 'cubic-bezier(.25,.8,.25,1)' });
    }
  }
}
return { step: at };
