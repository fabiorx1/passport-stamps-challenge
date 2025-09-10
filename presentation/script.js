function parseCSV(text) {
    const rows = [];
    let cur = [];
    let field = '';
    let i = 0;
    let inQuotes = false;
    while (i < text.length) {
        const ch = text[i];
        if (inQuotes) {
            if (ch === '"') {
                if (text[i+1] === '"') { field += '"'; i += 2; continue; }
                inQuotes = false; i++; continue;
            }
            field += ch; i++; continue;
        }
        if (ch === '"') { inQuotes = true; i++; continue; }
        if (ch === ',') { cur.push(field); field = ''; i++; continue; }
        if (ch === '\n' || ch === '\r') {
            // handle CRLF
            if (ch === '\r' && text[i+1] === '\n') i++;
            cur.push(field); field = '';
            rows.push(cur); cur = [];
            i++; continue;
        }
        field += ch; i++;
    }
    // last field
    if (field !== '' || cur.length > 0) cur.push(field);
    if (cur.length > 0) rows.push(cur);
    return rows;
}

// upload elements removed - loading default CSV instead
const fileInput = null;
const dropzone = null;
const tableContainer = document.getElementById('tableContainer');
const status = document.getElementById('status');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageInfo = document.getElementById('pageInfo');
const paginationControls = document.getElementById('paginationControls');
const reshuffleBtn = document.getElementById('reshuffleBtn');

let headers = [];
let entries = []; // original order
let shuffled = []; // used by paginated mode
const pageSize = 10;
let currentPage = 0;

function setStatus(msg, isError) {
    status.textContent = msg || '';
    status.className = isError ? 'error' : 'small';
}

function buildEntriesFromRows(rows) {
    if (!rows || rows.length === 0) return [];
    // Assume first row is header
    headers = rows[0].map(h => h || '');
    // If header is empty, create generic names
    headers = headers.map((h, idx) => h.trim() || `col_${idx}`);

    const data = [];
    for (let r = 1; r < rows.length; r++) {
        const row = rows[r];
        // skip empty rows
        if (row.length === 1 && row[0].trim() === '') continue;
        const obj = {};
        for (let c = 0; c < Math.max(headers.length, row.length); c++) {
            const key = headers[c] || `col_${c}`;
            obj[key] = row[c] !== undefined ? row[c] : '';
        }
        data.push(obj);
    }
    return data;
}

function renderTableRows(list) {
    // Wrap table in a horizontal-scrollable container so columns can overflow the viewport
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrapper';
    const table = document.createElement('table');
    // Ensure first header exists and is labeled as 'image'
    const firstHeader = 'image';
    const headerRow = [firstHeader, ...headers.slice(1)];

    // create a colgroup so column widths stay stable across pages
    const colgroup = document.createElement('colgroup');
    for (let i = 0; i < headerRow.length; i++) {
        const col = document.createElement('col');
        // fixed pixel widths for columns so they can overflow horizontally
        if (i === 1) col.style.width = '260px';
        else col.style.width = '200px';
        colgroup.appendChild(col);
    }
    table.appendChild(colgroup);

    const thead = document.createElement('thead');
    const trh = document.createElement('tr');
    for (const h of headerRow) {
        const th = document.createElement('th');
        th.textContent = h;
        trh.appendChild(th);
    }
    thead.appendChild(trh);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    for (const item of list) {
        const tr = document.createElement('tr');
        // first column -> image preview
        const tdImg = document.createElement('td');
        const img = document.createElement('img');
        img.className = 'preview';
        // try common first header key, but if not present use first property
        const imgSrc = item[headers[0]] !== undefined ? item[headers[0]] : item[Object.keys(item)[0]];
        img.src = imgSrc || '';
        img.alt = '';
        img.onerror = function() { this.style.opacity = 0.5; this.title = 'Failed to load'; };
        tdImg.appendChild(img);
        tr.appendChild(tdImg);

        // second column -> info field (if present)
        const tdInfo = document.createElement('td');
        const infoKey = headers.indexOf('info') !== -1 ? 'info' : headers[1] || `col_1`;
        tdInfo.textContent = item[infoKey] || '';
        tr.appendChild(tdInfo);

        // remaining columns
        for (let i = 2; i < headerRow.length; i++) {
            const td = document.createElement('td');
            const key = headers[i] || `col_${i}`;
            // Special-case: render the 6th column (index 5) as an image when present
            if (i === 6) {
                const img2 = document.createElement('img');
                img2.className = 'col-image';
                img2.src = item[key] || '';
                img2.alt = '';
                img2.onerror = function() { this.style.opacity = 0.5; this.title = 'Failed to load'; };
                td.appendChild(img2);
            } else {
                td.textContent = item[key] || '';
            }
            tr.appendChild(td);
        }
        tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    wrapper.appendChild(table);
    return wrapper;
}

function renderFull() {
    paginationControls.style.display = 'none';
    tableContainer.innerHTML = '';
    if (!entries.length) { setStatus('No data loaded'); return; }
    const tbl = renderTableRows(entries);
    tableContainer.appendChild(tbl);
    setStatus(`Showing all ${entries.length} rows`);
}

function shuffleArray(a) {
    const arr = a.slice();
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function renderPaginated() {
    paginationControls.style.display = '';
    if (!shuffled.length) { setStatus('No data loaded'); tableContainer.innerHTML = ''; return; }
    const totalPages = Math.ceil(shuffled.length / pageSize);
    if (currentPage < 0) currentPage = 0;
    if (currentPage >= totalPages) currentPage = totalPages - 1;
    const start = currentPage * pageSize;
    const end = Math.min(start + pageSize, shuffled.length);
    const slice = shuffled.slice(start, end);
    tableContainer.innerHTML = '';
    tableContainer.appendChild(renderTableRows(slice));
    pageInfo.textContent = `Page ${currentPage + 1} / ${totalPages} — showing ${start + 1} to ${end} of ${shuffled.length}`;
    setStatus('Paginated mode (shuffled order)');
}

function onModeChange() {
    const mode = document.querySelector('input[name="viewMode"]:checked').value;
    if (mode === 'full') renderFull(); else renderPaginated();
}

prevBtn.addEventListener('click', () => { currentPage--; onModeChange(); });
nextBtn.addEventListener('click', () => { currentPage++; onModeChange(); });
reshuffleBtn.addEventListener('click', () => { shuffled = shuffleArray(entries); currentPage = 0; onModeChange(); });

document.querySelectorAll('input[name="viewMode"]').forEach(r => r.addEventListener('change', () => { onModeChange(); }));

// Load default CSV on page load
window.addEventListener('load', () => {
    // fetch the bundled CSV file relative to this HTML
    fetch('data/stamps.csv').then(res => {
        if (!res.ok) throw new Error('Failed to fetch default CSV: ' + res.status);
        return res.text();
    }).then(text => {
        handleCSVText(text);
    }).catch(err => {
        setStatus(err.message, true);
    });
});

function handleCSVText(text) {
    try {
        const rows = parseCSV(text);
        entries = buildEntriesFromRows(rows);
        if (!entries.length) { setStatus('CSV parsed but no rows found', true); tableContainer.innerHTML = ''; return; }
        // prepare shuffled copy for paginated mode
        shuffled = shuffleArray(entries);
        currentPage = 0;
        onModeChange();
    } catch (err) {
        setStatus('Failed to parse CSV: ' + err.message, true);
    }
}

// upload handlers removed

function readFile(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) setStatus('Warning: file does not have .csv extension', false);
    const reader = new FileReader();
    reader.onload = (ev) => handleCSVText(ev.target.result);
    reader.onerror = () => setStatus('Failed to read file', true);
    reader.readAsText(file);
}