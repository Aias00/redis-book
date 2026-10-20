(() => {
  const saved = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const store = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  const theme = saved('redis-book-theme');
  if (theme === 'dark' || theme === 'light') document.documentElement.dataset.theme = theme;
  document.getElementById('theme').addEventListener('click', () => {
    const dark = document.documentElement.dataset.theme
      ? document.documentElement.dataset.theme === 'dark'
      : matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme = dark ? 'light' : 'dark';
    store('redis-book-theme', dark ? 'light' : 'dark');
  });
  const chapters = [...document.querySelectorAll('article > section')];
  const entries = [...document.querySelectorAll('article h1, article h2')].map(heading => {
    const section = heading.parentElement;
    return { title: heading.textContent, text: [...section.children].filter(node => node.tagName !== 'SECTION').map(node => node.textContent).join(' '), id: section.id };
  });
  const input = document.getElementById('search');
  const results = document.getElementById('results');
  input.addEventListener('input', () => {
    const query = input.value.trim().toLocaleLowerCase();
    results.replaceChildren();
    results.hidden = !query;
    document.getElementById('toc').hidden = Boolean(query);
    const matches = query ? entries.filter(entry => (entry.title + ' ' + entry.text).toLocaleLowerCase().includes(query)) : [];
    for (const entry of matches.slice(0, 40)) {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + entry.id;
      link.textContent = entry.title;
      item.append(link);
      results.append(item);
    }
    document.getElementById('search-status').textContent = query ? `找到 ${matches.length} 个段落${matches.length > 40 ? '，显示前 40 个' : ''}` : '';
  });
  const contents = document.getElementById('contents');
  if (matchMedia('(max-width:680px)').matches) contents.open = false;
  document.querySelector('aside').addEventListener('click', event => {
    if (event.target.closest('a') && matchMedia('(max-width:680px)').matches) contents.open = false;
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        store('redis-book-position', entry.target.id);
        document.querySelectorAll('#toc a').forEach(link => link.classList.toggle('active', decodeURIComponent(link.hash.slice(1)) === entry.target.id));
      }
    }, { rootMargin: '-10% 0px -70% 0px' });
    chapters.forEach(chapter => observer.observe(chapter));
  }
  const previous = saved('redis-book-position');
  if (!location.hash && previous && document.getElementById(previous)) {
    const link = document.createElement('a');
    link.href = '#' + previous;
    link.textContent = '继续上次阅读 →';
    document.querySelector('.intro').append(link);
  }
})();
