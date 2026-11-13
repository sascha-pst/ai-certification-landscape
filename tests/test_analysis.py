import unittest
from copy import deepcopy
from src.analysis import load, normalize, recommend, price_summary

class AnalysisTests(unittest.TestCase):
    def test_nested_grains_and_nulls(self):
        p = load()
        c, prices, modes = normalize(p)
        self.assertEqual(len(c), len(p['records']))
        self.assertEqual(len(prices), sum(len(r['price'] or []) for r in p['records']))
        self.assertEqual(len(modes), sum(len(r['delivery_modes'] or []) for r in p['records']))
        self.assertEqual(int(c.price_disclosed.sum()), sum(bool(r['price']) for r in p['records']))
        self.assertTrue(prices.amount.eq(0).any())
        self.assertEqual(int(price_summary(prices).price_rows.sum()), int(prices.amount.notna().sum()))

    def test_retrieval_eligibility_and_unknown_query(self):
        p = load()
        by_id = {r['id']: r for r in p['records']}
        hits = recommend('generative AI developer', p)
        self.assertTrue(hits)
        self.assertTrue(all(by_id[h['id']]['status'] == 'active' for h in hits))
        self.assertTrue(all(0 < h['similarity'] <= 1 for h in hits))
        self.assertEqual(recommend('zzzzzzunseenword', p), [])
        self.assertEqual(recommend('', p), [])
        self.assertEqual(hits, recommend('generative AI developer', p))

    def test_exact_query_retrieves_synthetic_match(self):
        p = deepcopy(load())
        p['records'] = [dict(p['records'][0], id='one', name='quasar robot', official_prep=None),
                        dict(p['records'][0], id='two', name='ocean coral', official_prep=None)]
        self.assertEqual(recommend('quasar robot', p)[0]['id'], 'one')

if __name__ == '__main__':
    unittest.main()
