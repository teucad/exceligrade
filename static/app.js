// Helper to create elements
function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const k in attrs) {
    if (k === 'class') e.className = attrs[k];
    else if (k === 'html') e.innerHTML = attrs[k];
    else e.setAttribute(k, attrs[k]);
  }
  for (const c of children) if (c) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  return e;
}

const classesContainer = document.getElementById('classesContainer');
const jsonInput = document.getElementById('jsonInput');


const themeToggle = document.getElementById('themeToggle');

function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  if (themeToggle) {
    themeToggle.textContent = theme === 'dark' ? '☀️ Light mode' : '🌙 Dark mode';
    themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
}

function initTheme() {
  const savedTheme = localStorage.getItem('exceligrade-theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  applyTheme(initialTheme);
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = document.body.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('exceligrade-theme', next);
  });
}

initTheme();


function updateJsonPreview() {
  const data = buildDataFromDOM();
  jsonInput.value = JSON.stringify(data, null, 2);
}

function buildDataFromDOM() {
  const classes = Array.from(classesContainer.querySelectorAll('.class-card')).map(card => {
    const name = card.querySelector('.class-name').value || 'Class';
    // collect rows, but ignore header row and empty placeholders so we don't send A/0 entries
    const assignments = Array.from(card.querySelectorAll('.assign-row'))
      .filter(r => !r.classList.contains('header'))
      .map(a => {
        const nmEl = a.querySelector('.assign-name');
        const wtEl = a.querySelector('.assign-weight');
        const cntEl = a.querySelector('.assign-count');
        const nm = nmEl ? nmEl.value.trim() : '';
        const wt = wtEl ? Number(wtEl.value) : 0;
        const cnt = cntEl ? Number(cntEl.value) : 1;
        return { name: nm || 'A', weight: wt || 0, count: cnt || 1 };
      })
      .filter(a => a.name !== '' && a.weight !== 0); // drop blank/zero rows

    return { name, assignments };
  });
  return { classes };
}

function addClass(prefill = null) {
  const card = el('section', { class: 'class-card' });

  const header = el('div', { class: 'class-row' },
    el('input', { type: 'text', class: 'class-name', placeholder: 'Class name' }),
    el('div', { class: 'subcontrols' },
      el('button', { class: 'icon-btn add-ass' }, el('span', {}, '+ Assignment')),
      el('button', { class: 'remove remove-class' }, 'Remove'))
  );

  const assigns = el('div', { class: 'assignments' },
    el('div', { class: 'assign-row header' },
       el('span', { class: 'assign-col assign-name' }, 'Assignment'),
       el('span', { class: 'assign-col assign-weight' }, 'Weight'),
       el('span', { class: 'assign-col assign-count' }, 'Count')
    )
  );

  card.appendChild(header);
  card.appendChild(assigns);

  classesContainer.appendChild(card);

  header.querySelector('.remove-class').addEventListener('click', () => { card.remove(); updateJsonPreview(); });
  header.querySelector('.add-ass').addEventListener('click', () => { addAssignment(card); updateJsonPreview(); });

  if (prefill) {
    card.querySelector('.class-name').value = prefill.name || '';
    (prefill.assignments || []).forEach(a => addAssignment(card, a));
  }

  return card;
}

function addAssignment(card, data = null) {
  const assigns = card.querySelector('.assignments');
  const row = el('div', { class: 'assign-row' },
    el('input', { type: 'text', class: 'assign-name', placeholder: 'Assignment name' }),
    el('input', { type: 'number', class: 'assign-weight', placeholder: 'Weight', min:0 }),
    el('input', { type: 'number', class: 'assign-count', placeholder: 'Count', min:1, value:1 }),
    el('button', { class: 'remove' }, 'Remove')
  );
  assigns.appendChild(row);

  row.querySelector('.remove').addEventListener('click', () => { row.remove(); updateJsonPreview(); });
  row.querySelector('.assign-name').addEventListener('input', updateJsonPreview);
  row.querySelector('.assign-weight').addEventListener('input', updateJsonPreview);
  row.querySelector('.assign-count').addEventListener('input', updateJsonPreview);

  if (data) {
    row.querySelector('.assign-name').value = data.name || '';
    row.querySelector('.assign-weight').value = data.weight || 0;
    if (data.count !== undefined) row.querySelector('.assign-count').value = data.count;
  }
}



document.getElementById('addClass').addEventListener('click', () => addClass());

document.getElementById('downloadJson').addEventListener('click', () => {
  let data;
  try {
    data = buildDataFromDOM();
  } catch (e) {
    alert('Could not build data: ' + e.message);
    return;
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'syllabus.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});

// Load JSON file (pre-made grade sheet)
document.getElementById('loadJsonBtn').addEventListener('click', () => {
  document.getElementById('jsonFileInput').click();
});

document.getElementById('jsonFileInput').addEventListener('change', (ev) => {
  const f = ev.target.files && ev.target.files[0];
  if (!f) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      if (!data || !Array.isArray(data.classes)) {
        alert('Invalid JSON: expected object with a "classes" array');
        return;
      }

      // clear existing classes
      classesContainer.innerHTML = '';

      // create classes from JSON
      data.classes.forEach(c => addClass(c));
      updateJsonPreview();
      alert('Loaded ' + (data.classes.length || 0) + ' classes from JSON');
    } catch (e) {
      alert('Failed to parse JSON: ' + e.message);
    }
  };
  reader.readAsText(f);
});

// Extract weights from uploaded syllabus file
document.getElementById('extractBtn').addEventListener('click', async () => {
  const input = document.getElementById('fileInput');
  if (!input.files || input.files.length === 0) { alert('Please choose a syllabus file (PDF, DOCX, or TXT).'); return; }
  const file = input.files[0];
  const fd = new FormData(); fd.append('file', file, file.name);

  try {
    const res = await fetch('/extract', { method: 'POST', body: fd });
    if (!res.ok) {
      // try to parse JSON error, otherwise fall back to text
      let message = res.statusText;
      try { const err = await res.json(); message = err.error || message; }
      catch (e) { try { const txt = await res.text(); message = txt.slice(0, 400); } catch(e2){} }
      alert('Error: ' + message);
      return;
    }
    let json;
    try { json = await res.json(); } catch (e) { alert('Extraction failed: invalid JSON returned'); return; }
    const assigns = json.assignments || [];
    assigns.forEach(a=> a.count = a.count || 1); // ensure count exists

    // display raw text for review
    if (json.text !== undefined) {
      const sec = document.querySelector('.extracted-text');
      document.getElementById('extractedText').value = json.text || '';
      sec.style.display = 'block';
    }

    if (assigns.length === 0) {
      alert('No assignment weights detected. See extracted text for help.');
      return;
    }

    // find last class card, or create one
    let card = addClass();

    // add extracted assignments to the new class
    assigns.forEach(a => addAssignment(card, { name: a.name, weight: a.weight }));
    updateJsonPreview();
    alert('Extracted ' + assigns.length + ' assignments and populated the last class.');
  } catch (e) { alert('Extraction failed: ' + e.message); }
});

async function doGenerate() {
  let data;
  try {
    data = buildDataFromDOM();
  } catch (e) {
    alert('Could not build data: ' + e.message);
    return;
  }
  try {
    const res = await fetch('/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) {
      let message = res.statusText;
      try { const err = await res.json(); message = err.error || message; }
      catch (e) { try { message = (await res.text()).slice(0, 400) || message; } catch (e2) {} }
      alert('Error: ' + message);
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'gradebook.xlsx'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  } catch (e) { alert('Request failed: ' + e.message); }
}

document.getElementById('generate').addEventListener('click', () => doGenerate());

// initialize with one example class
addClass({ name: 'Example Class', assignments: [{ name: 'HW', weight: 20, count: 4 }, { name: 'Exam', weight: 80, count: 2 }] });

updateJsonPreview();

