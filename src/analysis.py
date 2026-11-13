"""Offline cleaning, descriptive analysis and transparent TF-IDF retrieval."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from collections import Counter
from html import escape
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STOP = set('a an the and or of for to in on with is are as by this that certification certified certificate exam'.split())


def load(path=None):
    path = Path(path or ROOT / 'data/raw/credentials.json')
    payload = json.loads(path.read_text())
    records = payload['records']
    if payload['count'] != len(records):
        raise ValueError('Declared record count does not match data')
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate credential IDs')
    for r in records:
        if r['no_expiry'] is True and r['validity_months'] is not None:
            raise ValueError('Conflicting expiry information: ' + r['id'])
        for price in r['price'] or []:
            if price['amount'] is not None and price['amount'] < 0:
                raise ValueError('Negative price')
    return payload


def normalize(payload):
    """Keep one credential per row; prices and modes have separate grains."""
    credentials, prices, modes = [], [], []
    for record in payload['records']:
        r = record.copy()
        price_rows = r.pop('price')
        delivery = r.pop('delivery_modes')
        question = r.pop('question_count')
        r['question_min'] = question.get('min') if question else None
        r['question_max'] = question.get('max') if question else None
        r['price_disclosed'] = price_rows is not None and len(price_rows) > 0
        r['delivery_disclosed'] = delivery is not None
        r['expiry_category'] = ('no expiry stated' if r['no_expiry'] is True else
                                'fixed term stated' if r['validity_months'] is not None else 'not stated')
        for key, value in list(r.items()):
            if isinstance(value, (dict, list)):
                r[key] = json.dumps(value, ensure_ascii=False)
        credentials.append(r)
        for i, price in enumerate(price_rows or []):
            prices.append({'id': r['id'], 'price_row': i, 'issuer_name': r['issuer_name'],
                           'name': r['name'], 'status': r['status'], 'level': r['level'], **price})
        modes.extend({'id': r['id'], 'delivery_mode': m} for m in delivery or [])
    return pd.DataFrame(credentials), pd.DataFrame(prices), pd.DataFrame(modes)


def missingness(payload):
    rows = payload['records']
    return pd.DataFrame([{'field': f['name'], 'missing_count': sum(r.get(f['name']) is None for r in rows),
                          'missing_pct': 100 * sum(r.get(f['name']) is None for r in rows) / len(rows)}
                         for f in payload['fields']]).sort_values('missing_pct', ascending=False)


def price_summary(prices):
    """Descriptive price-row statistics, never a cheapest-credential ranking."""
    return (prices.groupby(['currency', 'billing', 'label', 'tax'], dropna=False)
            .agg(price_rows=('amount', 'count'), credentials=('id', 'nunique'),
                 minimum=('amount', 'min'), median=('amount', 'median'), maximum=('amount', 'max'))
            .reset_index())


def tokens(text):
    return [t for t in re.findall(r'[a-z][a-z0-9]+', text.lower()) if t not in STOP]


def recommend(query, payload, top_k=5, status='active'):
    """Cosine similarity over title, issuer, tier, kind and preparation text.

    Fits IDF on the eligible corpus only. No ratings or outcome claims.
    """
    rows = [r for r in payload['records'] if status is None or r['status'] == status]
    docs = [tokens(' '.join(str(r.get(k) or '') for k in
             ['name', 'issuer_name', 'level', 'kind', 'official_prep'])) for r in rows]
    vocab = sorted(set(t for d in docs for t in d))
    q = Counter(tokens(query))
    if not rows or not vocab or not set(q).intersection(vocab):
        return []
    idf = {t: np.log((1 + len(docs)) / (1 + sum(t in d for d in docs))) + 1 for t in vocab}
    def vector(counts):
        v = np.array([(1 + np.log(counts[t])) * idf[t] if counts[t] else 0 for t in vocab])
        norm = np.linalg.norm(v)
        return v / norm if norm else v
    qv = vector(q)
    scored = [(float(vector(Counter(d)) @ qv), r, d) for r, d in zip(rows, docs)]
    scored.sort(key=lambda item: (-item[0], item[1]['id']))
    return [{'id': r['id'], 'name': r['name'], 'issuer': r['issuer_name'],
             'similarity': round(score, 4), 'matched_terms': sorted(set(d) & set(q)), 'source_urls': r['source_urls']}
            for score, r, d in scored[:top_k] if score > 0]


def bar_svg(series, title, path):
    """Dependency-light exportable horizontal chart with explicit counts."""
    series = series.sort_values(ascending=True)
    height = 90 + len(series) * 30
    max_value = max(float(series.max()), 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img">',
             f'<title>{escape(title)}</title>', '<rect width="100%" height="100%" fill="#101b2c"/>',
             f'<text x="24" y="34" fill="#f5f7fb" font-size="21" font-family="sans-serif">{escape(title)}</text>']
    for i, (label, value) in enumerate(series.items()):
        y = 62 + i * 30
        w = 550 * float(value) / max_value
        parts.extend([f'<text x="24" y="{y+16}" fill="#cbd5e1" font-size="13" font-family="sans-serif">{escape(str(label))}</text>',
                      f'<rect x="320" y="{y}" width="{w}" height="21" rx="3" fill="#5eead4"/>',
                      f'<text x="{330+w}" y="{y+16}" fill="#f5f7fb" font-size="13" font-family="sans-serif">{value:g}</text>'])
    path.write_text('\n'.join(parts + ['</svg>']))


def run():
    payload = load()
    c, p, m = normalize(payload)
    out = ROOT / 'results'
    out.mkdir(exist_ok=True)
    for name, frame in [('credentials', c), ('prices', p), ('delivery_modes', m),
                        ('missingness', missingness(payload)), ('price_summary', price_summary(p))]:
        frame.to_csv(out / f'{name}.csv', index=False)
    bar_svg(c['issuer_name'].value_counts(), 'Credential counts by issuer · all snapshot statuses', out / 'issuers.svg')
    bar_svg(c['status'].value_counts(), 'Credential status · snapshot counts', out / 'statuses.svg')
    missing = missingness(payload).set_index('field')['missing_pct'].head(12)
    bar_svg(missing, 'Fields with the most nulls · percent of credentials', out / 'missingness.svg')
    metadata = {'source': 'https://github.com/jakeboland/ai-certifications-dataset',
                'canonical_source': payload['home'], 'generated_at': payload['generated_at'],
                'sha256': hashlib.sha256((ROOT / 'data/raw/credentials.json').read_bytes()).hexdigest(),
                'records': len(c), 'issuers': int(c['issuer'].nunique()), 'price_rows': len(p),
                'statuses': c['status'].value_counts().to_dict(),
                'price_disclosed_credentials': int(c['price_disclosed'].sum()),
                'null_means': payload['null_means']}
    (out / 'summary.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query')
    args = parser.parse_args()
    if args.query:
        print(json.dumps(recommend(args.query, load()), indent=2))
    else:
        run()
