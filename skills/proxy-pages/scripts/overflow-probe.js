// Paste into the console (or inject before </body>) to list elements that
// extend past the viewport. docScrollW > viewport means the page scrolls
// sideways; elements listed inside an overflow-x:auto box are fine.
(() => {
  const vw = document.documentElement.clientWidth;
  const out = [`viewport ${vw} docScrollW ${document.documentElement.scrollWidth}`];
  const seen = new Set();
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.right > vw + 1 && r.width > 0) {
      const cls = typeof el.className === 'string' ? el.className : (el.className && el.className.baseVal) || '';
      const k = `${el.tagName}.${cls}#${el.id}`;
      if (seen.has(k)) continue;
      seen.add(k);
      out.push(`${k} left=${Math.round(r.left)} right=${Math.round(r.right)} w=${Math.round(r.width)}`);
      if (out.length > 40) break;
    }
  }
  console.log(out.join('\n'));
  return out;
})();
