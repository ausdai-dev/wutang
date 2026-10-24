const fs = require('fs');
const content = fs.readFileSync('frontend/index.html', 'utf8');
const scripts = content.match(/<script[\s\S]*?<\/script>/gi);

scripts.forEach((s, i) => {
  const isJson = /type=["']application\/json["']/i.test(s);
  if (isJson) return;
  const code = s.replace(/^<script[^>]*>/i, '').replace(/<\/script>$/i, '');
  try {
    new Function(code);
    console.log(`Script ${i}: syntax OK (length ${code.length})`);
  } catch (err) {
    console.error(`Script ${i}: ERROR: ${err.message}`);
    // Locate error line
    const lines = code.split('\n');
    let okLine = 0;
    for (let j = 1; j <= lines.length; j++) {
      try {
        new Function(lines.slice(0, j).join('\n'));
        okLine = j;
      } catch (e) {
        if (!e.message.includes('Unexpected end of input')) {
          console.error(`First error around line ${j}: ${lines[j - 1]}`);
          console.error(e.stack);
          break;
        }
      }
    }
  }
});
