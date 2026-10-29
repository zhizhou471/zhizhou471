import argparse
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import benchmark


class FakeResponse(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


class HarnessTest(unittest.TestCase):
    def test_three_arms_are_independent_and_blinded(self):
        calls = []
        def fake_open(request, timeout):
            payload = json.loads(request.data)
            calls.append(payload)
            return FakeResponse(json.dumps({'choices':[{'message':{'content':'模拟响应，不是模型答案'}}], 'usage':{'total_tokens':9}}).encode())
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'OPENAI_API_KEY':'test-only'}), patch('urllib.request.urlopen', side_effect=fake_open):
            out = Path(temp) / 'mock-run'
            args = argparse.Namespace(mode='run', out=str(out), model='mock-model', url='http://mock.invalid', seed='test', timeout=1)
            benchmark.execute(args)
            self.assertEqual(len(calls), 30)
            self.assertTrue(all(len(c['messages']) == 2 for c in calls))
            blind = [json.loads(line) for line in (out/'blind.jsonl').read_text().splitlines()]
            self.assertEqual(len(blind), 30)
            self.assertTrue(all('arm' not in row and 'check' not in row for row in blind))
            key = json.loads((out/'key.json').read_text())
            self.assertEqual({r['id'] for r in blind}, set(key))
            self.assertEqual(len({r['id'] for r in blind}), 30)
            self.assertEqual(len((out/'scores.csv').read_text().splitlines()), 31)
            self.assertFalse(any('test-only' in p.read_text() for p in out.iterdir()))
            self.assertFalse(any('check' in c['messages'][1]['content'] for c in calls))

    def test_seed_is_deterministic(self):
        cases = json.loads((benchmark.HERE/'cases.json').read_text())
        self.assertEqual(benchmark.build_requests(cases, 'skill', 'seed'), benchmark.build_requests(cases, 'skill', 'seed'))

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            args=argparse.Namespace(mode='dry-run',out=temp,model=None,url='',seed='x',timeout=1)
            with self.assertRaises(FileExistsError): benchmark.execute(args)


if __name__ == '__main__': unittest.main()
