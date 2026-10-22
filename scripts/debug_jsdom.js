const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const HTML_PATH = path.join(__dirname, '..', 'frontend', 'index.html');
const html = fs.readFileSync(HTML_PATH, 'utf8');

const vc = new VirtualConsole();
vc.on('jsdomError', (e) => {
  console.error("JSDOM ERROR STACK:");
  console.error(e);
});
vc.on('error', (...a) => console.error("VC ERROR:", ...a));

try {
  const dom = new JSDOM(html, {
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    virtualConsole: vc,
  });
} catch (e) {
  console.error("TRY CATCH ERROR:", e);
}
