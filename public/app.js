const form = document.querySelector('#collector-form');
const message = document.querySelector('#message');
const resultsSection = document.querySelector('#results');
const resultList = document.querySelector('#result-list');
const submitButton = form.querySelector('button');
let latestResults = [];

function item(result) {
  const article = document.createElement('article');
  article.className = `result ${result.status}`;
  const url = document.createElement('p'); url.className = 'url'; url.textContent = result.url;
  const title = document.createElement('h3'); title.textContent = result.title || result.error || 'Unable to fetch title';
  article.append(url, title);
  return article;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const urls = document.querySelector('#urls').value.split('\n').map((url) => url.trim()).filter(Boolean);
  submitButton.disabled = true; message.textContent = 'Collecting titles…'; resultsSection.hidden = true;
  try {
    const response = await fetch('/api/collect', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ urls }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Collection failed.');
    latestResults = data.results;
    resultList.replaceChildren(...latestResults.map(item));
    resultsSection.hidden = false;
    message.textContent = `${latestResults.filter((result) => result.status === 'success').length} of ${latestResults.length} title(s) collected.`;
  } catch (error) { message.textContent = error.message; }
  finally { submitButton.disabled = false; }
});

document.querySelector('#download').addEventListener('click', () => {
  const report = JSON.stringify({ generated_at: new Date().toISOString(), results: latestResults }, null, 2);
  const link = Object.assign(document.createElement('a'), { href: URL.createObjectURL(new Blob([report], { type: 'application/json' })), download: 'titles.json' });
  link.click(); URL.revokeObjectURL(link.href);
});
